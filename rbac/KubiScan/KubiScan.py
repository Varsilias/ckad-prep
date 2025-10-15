import json
import logging
import os
import re
import sys
from argparse import ArgumentParser
import engine.utils
import engine.privleged_containers
from prettytable import PrettyTable, ALL
from engine.priority import Priority
from misc.colours import *
from misc import constants
import datetime
from api.api_client import api_init, running_in_container
from api.client_factory import ApiClientFactory
from api.config import set_api_client

json_filename = ""
output_file = ""
no_color = False
curr_header = ""
def get_color_by_priority(priority):
    color = WHITE
    if priority == Priority.CRITICAL:
        color = RED
    elif priority == Priority.HIGH:
        color = LIGHTYELLOW

    return color

def filter_objects_less_than_days(days, objects):
    filtered_objects= []
    current_datetime = datetime.datetime.now()
    for object in objects:
        if object.time:
            if (current_datetime.date() - object.time.date()).days < days:
                filtered_objects.append(object)

    objects = filtered_objects
    return objects

def filter_objects_by_priority(priority, objects):
    filtered_objects= []
    for object in objects:
        if object.priority.name == priority.upper():
            filtered_objects.append(object)
    objects = filtered_objects
    return objects

def get_delta_days_from_now(date):
    current_datetime = datetime.datetime.now()
    return (current_datetime.date() - date.date()).days

def print_all_risky_roles(show_rules=False, days=None, priority=None, namespace=None):
    risky_any_roles = engine.utils.get_risky_roles_and_clusterroles()
    if namespace is not None:
        logging.warning("'-rar' switch does not expect namespace ('-ns')\n")
    if days:
        risky_any_roles = filter_objects_less_than_days(int(days), risky_any_roles)
    if priority:
        risky_any_roles = filter_objects_by_priority(priority, risky_any_roles)
    generic_print('|Risky Roles and ClusterRoles|', risky_any_roles, show_rules)


def print_risky_roles(show_rules=False, days=None, priority=None, namespace=None):
    risky_roles = engine.utils.get_risky_roles()

    if days:
        risky_roles = filter_objects_less_than_days(int(days), risky_roles)
    if priority:
        risky_roles = filter_objects_by_priority(priority, risky_roles)

    filtered_risky_roles = []
    if namespace is None:
        generic_print('|Risky Roles |', risky_roles, show_rules)
    else:
        for risky_role in risky_roles:
            if risky_role.namespace == namespace:
                filtered_risky_roles.append(risky_role)
        generic_print('|Risky Roles |', filtered_risky_roles, show_rules)


def print_cve(certificate_authority_file=None, client_certificate_file=None, client_key_file=None, host=None):
    current_k8s_version = engine.utils.get_current_version(certificate_authority_file, client_certificate_file, client_key_file, host)
    if current_k8s_version is None:
        return
    cve_table = get_all_affecting_cves_table_by_version(current_k8s_version)
    print_table_aligned_left(cve_table)


def get_all_affecting_cves_table_by_version(current_k8s_version):
    cve_table = PrettyTable(['Severity', 'CVE Grade', 'CVE', 'Description', 'FixedVersions'])
    cve_table.hrules = ALL
    script_dir = os.path.dirname(__file__)
    cve_file = os.path.join(script_dir, 'CVE.json')
    with open(cve_file, 'r') as f:
        data = json.load(f)
    cves = data['CVES']
    for cve in cves:
        if curr_version_is_affected(cve, current_k8s_version):
            cve_description = split_cve_description(cve['Description'])
            fixed_version_list = get_fixed_versions_of_cve(cve["FixedVersions"])
            cve_color = get_cve_color(cve['Severity'])
            cve_table.add_row([cve_color + cve['Severity'] + WHITE, cve['Grade'], cve['CVENumber'], cve_description,
                       fixed_version_list])
    cve_table.sortby = "CVE Grade"
    cve_table.reversesort = True
    return cve_table

def get_cve_color(cve_severity):
    if cve_severity == "Low":
        return WHITE
    elif cve_severity == "Medium":
        return LIGHTYELLOW
    elif cve_severity == "High" or cve_severity == "Critical":
        return RED

def get_fixed_versions_of_cve(cve_fixed_versions):
    fixed_version_list = ""
    for fixed_version in cve_fixed_versions:
        fixed_version_list += fixed_version["Raw"] + "\n"
    return fixed_version_list[:-1]


def split_cve_description(cve_description):
    words = cve_description.split()
    res_description = ""
    words_in_row = 10
    for i, word in enumerate(words):
        if i % words_in_row == 0 and i != 0:
            res_description += "\n"
        res_description += word + " "
    return res_description[:-1]


def curr_version_is_affected(cve, current_k8s_version):
    max_fixed_version = find_max_fixed_version(cve)
    min_fixed_version = find_min_fixed_version(cve)
    # current_k8s_version < min_fixed_version
    if compare_versions(current_k8s_version, min_fixed_version) == -1:
        return True
    # current_k8s_version >= max_fixed_version
    if compare_versions(current_k8s_version, max_fixed_version) >= 0:
        return False
    for fixed_version in cve['FixedVersions']:
        if is_vulnerable_in_middle(current_k8s_version, fixed_version['Raw']):
            return True
    return False


def is_vulnerable_in_middle(current_k8s_version, cve_fixed_version):
    # Example: 1.15.2 -> [1, 15, 2]
    current_k8s_version_nums = [int(num) for num in current_k8s_version.split('.')]
    fixed_version_nums = [int(num) for num in cve_fixed_version.split('.')]
    if fixed_version_nums[0] == current_k8s_version_nums[0] and fixed_version_nums[1] == current_k8s_version_nums[1]:
        if fixed_version_nums[2] > current_k8s_version_nums[2]:
            return True
    return False


# version1 > version2 return 1
# version1 < version2 return -1
# version1 = version2 return 0

def sanitize_version(version):
    """Remove non-numeric suffixes from Kubernetes version strings."""
    return re.sub(r'[^0-9\.]', '', version.split('-')[0])

def compare_versions(version1, version2):
    version1 = sanitize_version(version1)
    version2 = sanitize_version(version2)
    version1_nums = [int(num) for num in version1.split('.')]
    version2_nums = [int(num) for num in version2.split('.')]
    for i in range(len(version2_nums)):
        if version2_nums[i] > version1_nums[i]:
            return -1
        elif version2_nums[i] < version1_nums[i]:
            return 1
    else:
        return 0


def find_max_fixed_version(cve):
    versions = []
    for fixed_version in cve['FixedVersions']:
        versions.append(fixed_version['Raw'])
    max_version = max(versions, key=lambda x: [int(num) for num in x.split('.')])
    return max_version

def find_min_fixed_version(cve):
    versions = []
    for fixed_version in cve['FixedVersions']:
        versions.append(fixed_version['Raw'])
    min_version = min(versions, key=lambda x: [int(num) for num in x.split('.')])
    return min_version

def print_risky_clusterroles(show_rules=False, days=None, priority=None, namespace=None):
    if namespace is not None:
        logging.warning("'-rcr' switch does not expect namespace ('-ns')\n")
    risky_clusterroles = engine.utils.get_risky_clusterroles()
    if days:
        risky_clusterroles = filter_objects_less_than_days(int(days), risky_clusterroles)
    if priority:
        risky_clusterroles = filter_objects_by_priority(priority, risky_clusterroles)
    generic_print('|Risky ClusterRoles |', risky_clusterroles, show_rules)

def print_all_risky_rolebindings(days=None, priority=None, namespace=None):
    if namespace is not None:
        logging.warning("'-rab' switch does not expect namespace ('-ns')\n")
    risky_any_rolebindings = engine.utils.get_all_risky_rolebinding()
    if days:
        risky_any_rolebindings = filter_objects_less_than_days(int(days), risky_any_rolebindings)
    if priority:
        risky_any_rolebindings = filter_objects_by_priority(priority, risky_any_rolebindings)
    generic_print('|Risky RoleBindings and ClusterRoleBindings|', risky_any_rolebindings)

def print_risky_rolebindings(days=None, priority=None, namespace=None):
    risky_rolebindings = engine.utils.get_risky_rolebindings()

    if days:
        risky_rolebindings = filter_objects_less_than_days(int(days), risky_rolebindings)
    if priority:
        risky_rolebindings = filter_objects_by_priority(priority, risky_rolebindings)

    if namespace is None:
        generic_print('|Risky RoleBindings|', risky_rolebindings)
    else:
        filtered_risky_rolebindings = []
        for risky_rolebinding in risky_rolebindings:
            if risky_rolebinding.namespace == namespace:
                filtered_risky_rolebindings.append(risky_rolebinding)
        generic_print('|Risky RoleBindings|', filtered_risky_rolebindings)

def print_risky_clusterrolebindings(days=None, priority=None, namespace=None):
    if namespace is not None:
        logging.warning("'-rcb' switch does not expect namespace ('-ns')\n")
    risky_clusterrolebindings = engine.utils.get_risky_clusterrolebindings()
    if days:
        risky_clusterrolebindings = filter_objects_less_than_days(int(days), risky_clusterrolebindings)
    if priority:
        risky_clusterrolebindings = filter_objects_by_priority(priority, risky_clusterrolebindings)
    generic_print('|Risky ClusterRoleBindings|', risky_clusterrolebindings)

def generic_print(header, objects, show_rules=False):
    roof = '+' + ('-' * (len(header)-2)) + '+'
    global curr_header
    curr_header = header
    print(roof)
    print(header)
    if show_rules:
        t = PrettyTable(['Priority', 'Kind', 'Namespace', 'Name', 'Creation Time', 'Rules'])
        for o in objects:
            if o.time is None:
                t.add_row([get_color_by_priority(o.priority) + o.priority.name + WHITE, o.kind, o.namespace, o.name, 'No creation time', get_pretty_rules(o.rules)])
            else:
                t.add_row([get_color_by_priority(o.priority) + o.priority.name + WHITE, o.kind, o.namespace, o.name, o.time.ctime() + " (" + str(get_delta_days_from_now(o.time)) + " days)", get_pretty_rules(o.rules)])
    else:
        t = PrettyTable(['Priority', 'Kind', 'Namespace', 'Name', 'Creation Time'])
        for o in objects:
            if o.time is None:
                t.add_row([get_color_by_priority(o.priority) + o.priority.name + WHITE, o.kind, o.namespace, o.name, 'No creation time'])
            else:
                t.add_row([get_color_by_priority(o.priority) + o.priority.name + WHITE, o.kind, o.namespace, o.name, o.time.ctime() + " (" + str(get_delta_days_from_now(o.time)) + " days)"])
    print_table_aligned_left(t)

def print_all_risky_containers(priority=None, namespace=None, read_token_from_container=False):
    pods = engine.utils.get_risky_pods(namespace, read_token_from_container)
    global curr_header
    curr_header = "|Risky Containers|"

    print("+----------------+")
    print("|Risky Containers|")
    t = PrettyTable(['Priority', 'PodName', 'Namespace', 'ContainerName', 'ServiceAccountNamespace', 'ServiceAccountName'])
    for pod in pods:
        if priority:
            pod.containers = filter_objects_by_priority(priority, pod.containers)
        for container in pod.containers:
            all_service_account = ''
            for service_account in container.service_accounts_name_set:
                all_service_account += service_account.user_info.name + ", "
            all_service_account = all_service_account[:-2]
            t.add_row([get_color_by_priority(container.priority)+container.priority.name+WHITE, pod.name, pod.namespace, container.name, container.service_account_namespace, all_service_account])

    print_table_aligned_left(t)


def get_rules_by_namespace(namespace=None):
    namespace_risky_roles = []
    risky_roles = engine.utils.get_risky_roles()
    for role in risky_roles:
        if role.namespace == namespace:
            return role
    return None

def print_all_risky_subjects(show_rules=False, priority=None, namespace=None):
    subjects = engine.utils.get_all_risky_subjects()
    if priority:
        subjects = filter_objects_by_priority(priority, subjects)
    global curr_header
    curr_header = "|Risky Users|"
    print("+-----------+")
    print("|Risky Users|")
    if show_rules:
        t = PrettyTable(['Priority', 'Kind', 'Namespace', 'Name', 'Rules'])
        for subject in subjects:
            if subject.user_info.namespace == namespace or namespace is None:
                subject_role = get_rules_by_namespace(subject.user_info.namespace)
                rules = subject_role.rules if subject_role else None
                t.add_row([get_color_by_priority(subject.priority)+subject.priority.name+WHITE, subject.user_info.kind, subject.user_info.namespace, subject.user_info.name,get_pretty_rules(rules)])
    else:
        t = PrettyTable(['Priority', 'Kind', 'Namespace', 'Name'])
        for subject in subjects:
            if subject.user_info.namespace == namespace or namespace is None:
                t.add_row([get_color_by_priority(subject.priority)+subject.priority.name+WHITE, subject.user_info.kind, subject.user_info.namespace, subject.user_info.name])

    print_table_aligned_left(t)

def print_all(days=None, priority=None, read_token_from_container=False):
    print_all_risky_roles(days=days, priority=priority)
    print_all_risky_rolebindings(days=days, priority=priority)
    print_all_risky_subjects(priority=priority)
    print_all_risky_containers(priority=priority, read_token_from_container=False)

def print_associated_rolebindings_to_role(role_name, namespace=None):
    associated_rolebindings = engine.utils.get_rolebindings_associated_to_role(role_name=role_name, namespace=namespace)

    print("Associated Rolebindings to Role \"{0}\":".format(role_name))
    t = PrettyTable(['Kind', 'Name', 'Namespace'])

    # TODO: merge them once the rolebinding.kind field won't be None
    for rolebinding in associated_rolebindings:
        t.add_row(['RoleBinding', rolebinding.metadata.name, rolebinding.metadata.namespace])

    print_table_aligned_left(t)


def print_associated_any_rolebindings_to_clusterrole(clusterrole_name):
    associated_rolebindings, associated_clusterrolebindings = engine.utils.get_rolebindings_and_clusterrolebindings_associated_to_clusterrole(role_name=clusterrole_name)

    print("Associated Rolebindings\ClusterRoleBinding to ClusterRole \"{0}\":".format(clusterrole_name))
    t = PrettyTable(['Kind', 'Name', 'Namespace'])

    for rolebinding in associated_rolebindings:
        t.add_row(['RoleBinding', rolebinding.metadata.name, rolebinding.metadata.namespace])

    for clusterrolebinding in associated_clusterrolebindings:
        t.add_row(['ClusterRoleBinding', clusterrolebinding.metadata.name, clusterrolebinding.metadata.namespace])

    print_table_aligned_left(t)

def print_associated_rolebindings_and_clusterrolebindings_to_subject(subject_name, kind, namespace=None):
    associated_rolebindings, associated_clusterrolebindings = engine.utils.get_rolebindings_and_clusterrolebindings_associated_to_subject(subject_name, kind, namespace)

    print("Associated Rolebindings\ClusterRoleBindings to subject \"{0}\":".format(subject_name))
    t = PrettyTable(['Kind', 'Name', 'Namespace'])

    for rolebinding in associated_rolebindings:
        t.add_row(['RoleBinding', rolebinding.metadata.name, rolebinding.metadata.namespace])

    for clusterrolebinding in associated_clusterrolebindings:
        t.add_row(['ClusterRoleBinding', clusterrolebinding.metadata.name, clusterrolebinding.metadata.namespace])

    print_table_aligned_left(t)

def desrialize_token(token):
    desirialized_token = ''
    for key in token.keys():
        desirialized_token += key + ': ' + token[key]
        desirialized_token += '\n'
    return desirialized_token

def dump_tokens_from_pods(pod_name=None, namespace=None, read_token_from_container=False):
    if pod_name is not None:
        pods_with_tokens = engine.utils.dump_pod_tokens(pod_name, namespace, read_token_from_container)
    else:
        pods_with_tokens = engine.utils.dump_all_pods_tokens_or_by_namespace(namespace, read_token_from_container)

    t = PrettyTable(['PodName',  'Namespace', 'ContainerName', 'Decoded Token'])
    for pod in pods_with_tokens:
        for container in pod.containers:
            new_token = desrialize_token(container.token)
            t.add_row([pod.name, pod.namespace, container.name, new_token])

    print_table_aligned_left(t)


def print_subjects_by_kind(kind):
    subjects = engine.utils.get_subjects_by_kind(kind)
    print('Subjects (kind: {0}) from all rolebindings:'.format(kind))
    t = PrettyTable(['Kind', 'Namespace', 'Name'])
    for subject in subjects:
        t.add_row([subject.kind, subject.namespace, subject.name])

    print_table_aligned_left(t)
    print('Total number: %s' % len(subjects))

def get_pretty_rules(rules):
    pretty = ''
    if rules is not None:
        for rule in rules:
            verbs_string = '('
            for verb in rule.verbs:
                verbs_string += verb + ','
            verbs_string = verbs_string[:-1]
            verbs_string += ')->'

            resources_string = '('
            if rule.resources is None:
                resources_string += 'None'
            else:
                for resource in rule.resources:
                    resources_string += resource + ','

                resources_string = resources_string[:-1]
            resources_string += ')\n'
            pretty += verbs_string + resources_string
    return pretty

def print_rolebinding_rules(rolebinding_name, namespace):
    role = engine.utils.get_rolebinding_role(rolebinding_name, namespace)
    print("RoleBinding '{0}\{1}' rules:".format(namespace, rolebinding_name))
    t = PrettyTable(['Kind', 'Namespace', 'Name', 'Rules'])
    t.add_row([role.kind, role.metadata.namespace, role.metadata.name, get_pretty_rules(role.rules)])

    print_table_aligned_left(t)

def print_clusterrolebinding_rules(cluster_rolebinding_name):
    cluster_role = engine.utils.get_clusterrolebinding_role(cluster_rolebinding_name)
    print("ClusterRoleBinding '{0}' rules:".format(cluster_rolebinding_name))
    t = PrettyTable(['Kind', 'Namespace', 'Name', 'Rules'])
    t.add_row([cluster_role.kind, cluster_role.metadata.namespace, cluster_role.metadata.name, get_pretty_rules(cluster_role.rules)])

    print_table_aligned_left(t)

def print_rules_associated_to_subject(name, kind, namespace=None):
    roles = engine.utils.get_roles_associated_to_subject(name, kind, namespace)
    print("Roles associated to Subject '{0}':".format(name))
    t = PrettyTable(['Kind', 'Namespace', 'Name', 'Rules'])
    for role in roles:
        t.add_row([role.kind, role.metadata.namespace, role.metadata.name, get_pretty_rules(role.rules)])

    print_table_aligned_left(t)

# https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#create-a-pod-that-has-access-to-the-secret-data-through-a-volume
def print_pods_with_access_secret_via_volumes(namespace=None):
    pods = engine.utils.list_pods_for_all_namespaces_or_one_namspace(namespace)

    print("Pods with access to secret data through volumes:")
    t = PrettyTable(['Pod Name', 'Namespace', 'Container Name', 'Volume Mounted Secrets'])
    for pod in pods.items:
        for container in pod.spec.containers:
            mount_info = ''
            secrets_num = 1
            if container.volume_mounts is not None:
                for volume_mount in container.volume_mounts:
                    for volume in pod.spec.volumes:
                        if volume.secret is not None and volume.name == volume_mount.name:
                            #mount_info += 'Mounted path: {0}\nSecret name: {1}\nVolume name: {2}\n'.format(volume_mount.mount_path, volume.secret.secret_name, volume.name)
                            mount_info += '{2}. Mounted path: {0}\n   Secret name: {1}\n'.format(volume_mount.mount_path, volume.secret.secret_name, secrets_num)
                            secrets_num += 1
                if mount_info != '':
                    t.add_row([pod.metadata.name, pod.metadata.namespace, container.name, mount_info])

    print_table_aligned_left(t)

# https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#create-a-pod-that-has-access-to-the-secret-data-through-environment-variables
def print_pods_with_access_secret_via_environment(namespace=None):
    pods = engine.utils.list_pods_for_all_namespaces_or_one_namspace(namespace)

    print("Pods with access to secret data through environment:")
    t = PrettyTable(['Pod Name', 'Namespace', 'Container Name', 'Environment Mounted Secrets'])
    for pod in pods.items:
        for container in pod.spec.containers:
            mount_info = ''
            secrets_num = 1
            if container.env is not None:
                for env in container.env:
                    if env.value_from is not None and env.value_from.secret_key_ref is not None:
                        mount_info += '{2}. Environment variable name: {0}\n   Secret name: {1}\n'.format(env.name, env.value_from.secret_key_ref.name, secrets_num)
                        secrets_num += 1
                if mount_info != '':
                    t.add_row([pod.metadata.name, pod.metadata.namespace, container.name, mount_info])

    print_table_aligned_left(t)

def parse_security_context(security_context):
    is_header_set = False
    context = ''
    if security_context:
        dict =  security_context.to_dict()
        for key in dict.keys():
            if dict[key] is not None:
                if not is_header_set:
                    context += "SecurityContext:\n"
                    is_header_set = True
                context += '  {0}: {1}\n'.format(key, dict[key])
    return context

def parse_container_spec(container_spec):
    spec = ''
    dict =  container_spec.to_dict()
    is_ports_header_set = False
    for key in dict.keys():
        if dict[key] is not None:
            if key == 'ports':
                if not is_ports_header_set:
                    spec += "Ports:\n"
                    is_ports_header_set = True
                for port_obj in dict[key]:
                    if 'host_port' in port_obj:
                        spec += '  {0}: {1}\n'.format('container_port', port_obj['container_port'])
                        spec += '  {0}: {1}\n'.format('host_port', port_obj['host_port'])
                        break
    spec += parse_security_context(container_spec.security_context)
    return spec

def parse_pod_spec(pod_spec, container):
    spec = ''
    dict =  pod_spec.to_dict()
    is_volumes_header_set = False
    for key in dict.keys():
        if dict[key] is not None:
            if key == 'host_pid' or key == 'host_ipc' or key == 'host_network':
                spec += '{0}: {1}\n'.format(key, dict[key])

            if key == 'volumes' and container.volume_mounts is not None:
                for volume_obj in dict[key]:
                    if 'host_path' in volume_obj:
                        if volume_obj['host_path']:
                            for volume_mount in container.volume_mounts:
                                if volume_obj['name'] == volume_mount.name:
                                    if not is_volumes_header_set:
                                        spec += "Volumes:\n"
                                        is_volumes_header_set = True
                                    spec += '  -{0}: {1}\n'.format('name', volume_obj['name'])
                                    spec += '   host_path:\n'
                                    spec += '     {0}: {1}\n'.format('path', volume_obj['host_path']['path'])
                                    spec += '     {0}: {1}\n'.format('type', volume_obj['host_path']['type'])
                                    spec += '     {0}: {1}\n'.format('container_path', volume_mount.mount_path)

    spec += parse_security_context(pod_spec.security_context)
    return spec

def print_privileged_containers(namespace=None):
    global curr_header
    curr_header = "|Privileged Containers|"
    print("+---------------------+")
    print("|Privileged Containers|")
    t = PrettyTable(['Pod', 'Namespace', 'Pod Spec', 'Container', 'Container info'])
    pods = engine.privleged_containers.get_privileged_containers(namespace)
    for pod in pods:
        for container in pod.spec.containers:
            t.add_row([pod.metadata.name, pod.metadata.namespace, parse_pod_spec(pod.spec, container), container.name, parse_container_spec(container)])

    print_table_aligned_left(t)

def print_join_token():
    import os
    from kubernetes.client import Configuration
    master_ip = Configuration().host.split(':')[1][2:]
    master_port = Configuration().host.split(':')[2]

    ca_cert = '/etc/kubernetes/pki/ca.crt'
    if not os.path.exists(ca_cert):
        ca_cert = '/etc/kubernetes/ca.crt'

        
    if running_in_container():
        ca_cert = os.getenv('KUBISCAN_VOLUME_PATH', '/tmp') + ca_cert

    join_token_path = os.path.dirname(os.path.realpath(__file__)) + '/engine/join_token.sh'
    tokens = engine.utils.list_boostrap_tokens_decoded()

    if not tokens:
        print("No bootstrap tokens exist")
    else:
        for token in tokens:
            command = 'sh ' + join_token_path + ' ' + ' '.join([master_ip, master_port, ca_cert, token])
            print('\nExecute: %s' % command)
            os.system(command)

def print_logo():
    logo = '''
                   `-/osso/-`                    
                `-/osssssssssso/-`                
            .:+ssssssssssssssssssss+:.            
        .:+ssssssssssssssssssssssssssss+:.        
     :osssssssssssssssssssssssssssssssssssso:     
    /sssssssssssss+::osssssso::+sssssssssssss+    
   `sssssssssso:--..-`+ssss+ -..--:ossssssssss`   
   /sssssssss:.+ssss/ /ssss/ /ssss+.:sssssssss/   
  `ssssssss:.+sssssss./ssss/`sssssss+.:ssssssss`  
  :ssssss/`-///+oss+/`-////-`/+sso+///-`/ssssss/  
  sssss+.`.-:-:-..:/`-++++++-`/:..-:-:-.`.+sssss` 
 :ssso..://:-`:://:.. osssso ..://::`-://:..osss: 
 osss`-/-.`-- :.`.-/. /ssss/ ./-.`-: --`.-/-`osso 
-sss:`//..-`` .`-`-//`.----. //-`-`. ``-..//.:sss-
osss:.::`...`- ..`.:/`+ssss+`/:``.. -`...`::.:ssso
+ssso`:/:`--`:`--`/:-`ssssss`-//`--`:`--`:/:`osss+
 :sss+`-//.`...`-//..osssssso..//-`...`.//-`+sss: 
  `+sss/...::/::..-+ssssssssss+-..::/::.../sss+`  
    -ossss+/:::/+ssssssssssssssss+/:::/+sssso-    
      :ssssssssssssssssssssssssssssssssssss/      
       `+ssssssssssssssssssssssssssssssss+`       
         -osssssssssssssssssssssssssssss-         
          `/ssssssssssssssssssssssssss/`       
    
               KubiScan version 1.7
               Author: Eviatar Gerzi
    '''
    print(logo)

def print_examples():
    import os
    with open(os.path.dirname(os.path.realpath(__file__)) + '/examples/examples.txt', 'r') as f:
        print(f.read())

def main():
    opt = ArgumentParser(description='KubiScan.py - script used to get information on risky permissions on Kubernetes', usage="""KubiScan.py [options...]

This tool can get information about risky roles\clusterroles, rolebindings\clusterrolebindings, users and pods.
Use "KubiScan.py -h" for help or "KubiScan.py -e" to see examples.
Requirements:
    - Python 3
    - Kubernetes python client (https://github.com/kubernetes-client/python) 
      Can be installed:
            From source:
                git clone --recursive https://github.com/kubernetes-client/python.git
                cd python
                python setup.py install
            From PyPi directly:
                pip3 install kubernetes
    - Prettytable
        pip3 install PTable
    """)
    opt.add_argument('-f', '--file', type=str, help='File path for static API client. Providing this will automatically use a static scan.')

    opt.add_argument('-rr', '--risky-roles', action='store_true', help='Get all risky Roles (can be used with -r to view rules)', required=False)
    opt.add_argument('-rcr', '--risky-clusterroles', action='store_true', help='Get all risky ClusterRoles (can be used with -r to view rules)',required=False)
    opt.add_argument('-rar', '--risky-any-roles', action='store_true', help='Get all risky Roles and ClusterRoles', required=False)

    opt.add_argument('-rb', '--risky-rolebindings', action='store_true', help='Get all risky RoleBindings', required=False)
    opt.add_argument('-rcb', '--risky-clusterrolebindings', action='store_true',help='Get all risky ClusterRoleBindings', required=False)
    opt.add_argument('-rab', '--risky-any-rolebindings', action='store_true', help='Get all risky RoleBindings and ClusterRoleBindings', required=False)

    opt.add_argument('-rs', '--risky-subjects', action='store_true',help='Get all risky Subjects (Users, Groups or Service Accounts)', required=False)
    opt.add_argument('-rp', '--risky-pods', action='store_true', help='Get all risky Pods\Containers.\n'
                                                                      'Use the -d\--deep switch to read the tokens from the current running containers', required=False)
    opt.add_argument('-d', '--deep', action='store_true', help='Works only with -rp\--risky-pods switch. If this is specified, it will execute each pod to get its token.\n'
                                                               'Without it, it will read the pod mounted service account secret from the ETCD, it less reliable but much faster.', required=False)
    opt.add_argument('-pp', '--privleged-pods', action='store_true', help='Get all privileged Pods\Containers.',  required=False)
    opt.add_argument('-a', '--all', action='store_true',help='Get all risky Roles\ClusterRoles, RoleBindings\ClusterRoleBindings, users and pods\containers', required=False)
    opt.add_argument('-cve', '--cve', action='store_true', help=f"Scan of CVE's", required=False)
    opt.add_argument('-jt', '--join-token', action='store_true', help='Get join token for the cluster. OpenSsl must be installed + kubeadm', required=False)
    opt.add_argument('-psv', '--pods-secrets-volume', action='store_true', help='Show all pods with access to secret data throught a Volume', required=False)
    opt.add_argument('-pse', '--pods-secrets-env', action='store_true', help='Show all pods with access to secret data throught a environment variables', required=False)
    opt.add_argument('-ctx', '--context', action='store', help='Context to run. If none, it will run in the current context.', required=False)
    opt.add_argument('-p', '--priority', action='store', help='Filter by priority (CRITICAL\HIGH\LOW)', required=False)


    helper_switches = opt.add_argument_group('Helper switches')
    helper_switches.add_argument('-lt', '--less-than', action='store', metavar='NUMBER', help='Used to filter object exist less than X days.\nSupported on Roles\ClusterRoles and RoleBindings\ClusterRoleBindings.'
                                                                                              'IMPORTANT: If object does not have creation time (usually in ClusterRoleBindings), omit this switch to see it.', required=False)

    helper_switches.add_argument('-ns', '--namespace', action='store', help='If present, the namespace scope that will be used', required=False)
    helper_switches.add_argument('-k', '--kind', action='store', help='Kind of the object', required=False)
    helper_switches.add_argument('-r', '--rules', action='store_true', help='Show rules. Supported only on pinrting risky Roles\ClusterRoles.', required=False)
    helper_switches.add_argument('-e', '--examples', action='store_true', help='Show examples.', required=False)
    helper_switches.add_argument('-n', '--name', action='store', help='Name', required=False)
    dumping_tokens = opt.add_argument_group('Dumping tokens', description='Use the switches: name (-n\--name) or namespace (-ns\ --namespace)')
    dumping_tokens.add_argument('-dt', '--dump-tokens', action='store_true', help='Dump tokens from pod\pods\n'
                                                                                  'Example: -dt OR -dt -ns \"kube-system\"\n'
                                                                                  '-dt -n \"nginx1\" -ns \"default\"', required=False)

    helper_switches = opt.add_argument_group('Remote switches')
    helper_switches.add_argument('-ho', '--host', action='store', metavar='<MASTER_IP>:<PORT>', help='Host contain the master ip and port.\n'
                                                                                                     'For example: 10.0.0.1:6443', required=False)
    helper_switches.add_argument('-c', '--cert-filename', action='store', metavar='CA_FILENAME', help='Certificate authority path (\'/../ca.crt\'). If not specified it will try without SSL verification.\n'
                                                                            'Inside Pods the default location is \'/var/run/secrets/kubernetes.io/serviceaccount/ca.crt\''
                                                                            'Or \'/run/secrets/kubernetes.io/serviceaccount/ca.crt\'.', required=False)
    helper_switches.add_argument('-cc', '--client-certificate', action='store', metavar='CA_FILENAME',
                                 help='Path to client key file', required=False)
    helper_switches.add_argument('-ck', '--client-key', action='store', metavar='CA_FILENAME',
                                 help='Path to client certificate file', required=False)

    helper_switches.add_argument('-co', '--kube-config', action='store', metavar='KUBE_CONFIG_FILENAME',
                                 help='The kube config file.\n'
                                      'For example: ~/.kube/config', required=False)
        
    helper_switches.add_argument('-t', '--token-filename', action='store', metavar='TOKEN_FILENAME',
                                 help='A bearer token. If this token does not have the required permissions for this application,'
                                      'the application will faill to get some of the information.\n'
                                      'Minimum required permissions:\n'
                                      '- resources: [\"roles\", \"clusterroles\", \"rolebindings\", \"clusterrolebindings\", \"pods\", \"secrets\"]\n'
                                      '  verbs: [\"get\", \"list\"]\n'
                                      '- resources: [\"pods/exec\"]\n'
                                      '  verbs: [\"create\"]')
    helper_switches.add_argument('-o', '--output-file', metavar='OUTPUT_FILENAME', help='Path to output file')
    helper_switches.add_argument('-q', '--quiet', action='store_true', help='Hide the banner')
    helper_switches.add_argument('-j', '--json', metavar='JSON_FILENAME', help='Export to json')
    helper_switches.add_argument('-nc', '--no-color', action='store_true', help='Print without color')
    associated_rb_crb_to_role = opt.add_argument_group('Associated RoleBindings\ClusterRoleBindings to Role', description='Use the switch: namespace (-ns\--namespace).')
    associated_rb_crb_to_role.add_argument('-aarbr', '--associated-any-rolebindings-role', action='store', metavar='ROLE_NAME',
                                           help='Get associated RoleBindings\ClusterRoleBindings to a specific role\n'
                                                'Example: -aarbr \"read-secrets-role\" -ns \"default\"', required=False)

    associated_rb_crb_to_clusterrole = opt.add_argument_group('Associated RoleBindings\ClusterRoleBindings to ClusterRole')
    associated_rb_crb_to_clusterrole.add_argument('-aarbcr', '--associated-any-rolebindings-clusterrole', action='store', metavar='CLUSTERROLE_NAME',
                                                  help='Get associated RoleBindings\ClusterRoleBindings to a specific role\n'
                                                       'Example:  -aarbcr \"read-secrets-clusterrole\"', required=False)


    associated_rb_crb_to_subject = opt.add_argument_group('Associated RoleBindings\ClusterRoleBindings to Subject (user, group or service account)',
                                                           description='Use the switches: namespace (-ns\--namespace) and kind (-k\--kind).\n')
    associated_rb_crb_to_subject.add_argument('-aarbs', '--associated-any-rolebindings-subject', action='store', metavar='SUBJECT_NAME',
                                              help='Get associated Rolebindings\ClusterRoleBindings to a specific Subject (user, group or service account)\n'
                                                   'Example: -aarbs \"system:masters\" -k \"Group\"', required=False)

    associated_rb_crb_to_subject = opt.add_argument_group('Associated Roles\ClusterRoles to Subject (user, group or service account)',
                                                           description='Use the switches: namespace (-ns\--namespace) and kind (-k\--kind).\n')
    associated_rb_crb_to_subject.add_argument('-aars', '--associated-any-roles-subject', action='store', metavar='SUBJECT_NAME',
                                              help='Get associated Roles\ClusterRoles to a specific Subject (user, group or service account)\n'
                                                   'Example: -aars \"generic-garbage-collector\" -k \"ServiceAccount\" -ns \"kube-system\"', required=False)

    list_subjects = opt.add_argument_group('List Subjects')
    list_subjects.add_argument('-su', '--subject-users', action='store_true', help='Get Subjects with User kind', required=False)
    list_subjects.add_argument('-sg', '--subject-groups', action='store_true', help='Get Subjects with Group kind', required=False)
    list_subjects.add_argument('-ss', '--subject-serviceaccounts', action='store_true', help='Get Subjects with ServiceAccount kind', required=False)


    list_rules = opt.add_argument_group('List rules of RoleBinding\ClusterRoleBinding')
    list_rules.add_argument('-rru', '--rolebinding-rules', action='store', metavar='ROLEBINDING_NAME', help='Get rules of RoleBinding', required=False)
    list_rules.add_argument('-crru', '--clusterrolebinding-rules', action='store', metavar='CLUSTERROLEBINDING_NAME',  help='Get rules of ClusterRoleBinding',required=False)

    args = opt.parse_args()
    if args.no_color:
        global no_color
        no_color = True
    if args.json:
        global json_filename
        json_filename = args.json
        
    if args.output_file:
        f = open(args.output_file, 'w')
        sys.stdout = f
    if not args.quiet:
        print_logo()

    if args.examples:
        print_examples()
        exit()


    if args.file:
        api_client = ApiClientFactory.get_client(use_static=True, input_file=args.file)
    else:
        api_client = ApiClientFactory.get_client(use_static=False)
        api_init(kube_config_file=args.kube_config, host=args.host, token_filename=args.token_filename, cert_filename=args.cert_filename, context=args.context)
    
    set_api_client(api_client)


    if args.cve:
        print_cve(args.cert_filename, args.client_certificate, args.client_key, args.host)
    if args.risky_roles:
        print_risky_roles(show_rules=args.rules, days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_clusterroles:
        print_risky_clusterroles(show_rules=args.rules, days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_any_roles:
        print_all_risky_roles(show_rules=args.rules, days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_rolebindings:
        print_risky_rolebindings(days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_clusterrolebindings:
        print_risky_clusterrolebindings(days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_any_rolebindings:
        print_all_risky_rolebindings(days=args.less_than, priority=args.priority, namespace=args.namespace)
    if args.risky_subjects:
        print_all_risky_subjects(show_rules=args.rules,priority=args.priority, namespace=args.namespace)
    if args.risky_pods:
        if args.deep and args.file:
            print('Cannot access pods token in a static scan. In static scan use -rp only.')
        else:
            print_all_risky_containers(priority=args.priority, namespace=args.namespace, read_token_from_container=args.deep)
    if args.all:
        print_all(days=args.less_than, priority=args.priority, read_token_from_container=args.deep)
    elif args.privleged_pods:
        print_privileged_containers(namespace=args.namespace)
    elif args.join_token:
        print_join_token()
    elif args.pods_secrets_volume:
        if args.namespace:
            print_pods_with_access_secret_via_volumes(namespace=args.namespace)
        else:
            print_pods_with_access_secret_via_volumes()
    elif args.pods_secrets_env:
        if args.namespace:
            print_pods_with_access_secret_via_environment(namespace=args.namespace)
        else:
            print_pods_with_access_secret_via_environment()
    elif args.associated_any_rolebindings_role:
        if args.namespace:
            print_associated_rolebindings_to_role(args.associated_any_rolebindings_role, args.namespace)
    elif args.associated_any_rolebindings_clusterrole:
        print_associated_any_rolebindings_to_clusterrole(args.associated_any_rolebindings_clusterrole)
    elif args.associated_any_rolebindings_subject:
        if args.kind:
            if args.kind == constants.SERVICEACCOUNT_KIND:
                if args.namespace:
                    print_associated_rolebindings_and_clusterrolebindings_to_subject(args.associated_any_rolebindings_subject, args.kind, args.namespace)
                else:
                    print('For ServiceAccount kind specify namespace (-ns, --namespace)')
            else:
                print_associated_rolebindings_and_clusterrolebindings_to_subject(args.associated_any_rolebindings_subject, args.kind)
        else:
            print('Subject namespace (-ns, --namespace) or kind (-k, --kind) was not specificed')
    elif args.associated_any_roles_subject:
        if args.kind:
            if args.kind == constants.SERVICEACCOUNT_KIND:
                if args.namespace:
                    print_rules_associated_to_subject(args.associated_any_roles_subject, args.kind, args.namespace)
                else:
                    print('For ServiceAccount kind specify namespace (-ns, --namespace)')
            else:
                print_rules_associated_to_subject(args.associated_any_roles_subject, args.kind)
        else:
            print("Please specify kind (-k, --kind).")
    elif args.dump_tokens:
        if args.name:
            if args.namespace:
                dump_tokens_from_pods(pod_name=args.name, namespace=args.namespace, read_token_from_container=args.deep)
            else:
                print('When specificing Pod name, need also namespace')
        elif args.namespace:
            dump_tokens_from_pods(namespace=args.namespace, read_token_from_container=args.deep)
        else:
            dump_tokens_from_pods(read_token_from_container=args.deep)
    elif args.subject_users:
        print_subjects_by_kind(constants.USER_KIND)
    elif args.subject_groups:
        print_subjects_by_kind(constants.GROUP_KIND)
    elif args.subject_serviceaccounts:
        print_subjects_by_kind(constants.SERVICEACCOUNT_KIND)
    elif args.rolebinding_rules:
        if args.namespace:
            print_rolebinding_rules(args.rolebinding_rules, args.namespace)
        else:
            print("Namespace was not specified")
    elif args.clusterrolebinding_rules:
        print_clusterrolebinding_rules(args.clusterrolebinding_rules)

def print_table_aligned_left(table):
    global json_filename
    if json_filename != "":
        export_to_json(table, json_filename)
    global output_file
    if no_color:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        for row in table._rows:
            row[0] = ansi_escape.sub('', row[0])

    table.align = 'l'
    print(table)
    print('\n')


def export_to_json(table, json_filename):
    global curr_header
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    headers = table.field_names
    curr_header = curr_header.replace("|", "")
    data = {curr_header: []}
    try:
        with open(json_filename, "r") as json_file:
            json_file_content = json_file.read()
    except:
        json_file_content = ""

    res = [] if json_file_content == "" else json.loads(json_file_content)
    json_file = open(json_filename, "w+")
    for row_index, row in enumerate(table._rows):
        curr_item = {}
        for i, entity in enumerate(row):
            entity_without_color = ansi_escape.sub('', entity) if headers[i] == 'Priority' else entity
            # curr_item.update({headers[i]: entity_without_color})
            curr_item[headers[i]] = entity_without_color

        data[curr_header].append(curr_item)
    res.append(data)
    json_file.write(json.dumps(res, indent=2))
    json_file.flush()
    json_file.close()


if __name__ == '__main__':
    main()
