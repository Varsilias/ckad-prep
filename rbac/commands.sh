git clone git@github.com:cyberark/KubiScan.git
pip3 install kubernetes PTable
pip install -r requirements.txt
python KubiScan.py -e
python KubiScan.py --risky-roles
Using kube config file.
+------------+
|Risky Roles |
+----------+------+-------------+------------------------------------+-----------------------------------+
| Priority | Kind | Namespace   | Name                               | Creation Time                     |
+----------+------+-------------+------------------------------------+-----------------------------------+
| CRITICAL | Role | kube-system | system:controller:bootstrap-signer | Fri Oct 10 08:57:58 2025 (4 days) |
| CRITICAL | Role | kube-system | system:controller:token-cleaner    | Fri Oct 10 08:57:58 2025 (4 days) |
+----------+------+-------------+------------------------------------+-----------------------------------+
python KubiScan.py --risky-any-roles
Using kube config file.
+----------------------------+
|Risky Roles and ClusterRoles|
+----------+-------------+-------------+---------------------------------------------+-----------------------------------+
| Priority | Kind        | Namespace   | Name                                        | Creation Time                     |
+----------+-------------+-------------+---------------------------------------------+-----------------------------------+
| CRITICAL | Role        | kube-system | system:controller:bootstrap-signer          | Fri Oct 10 08:57:58 2025 (4 days) |
| CRITICAL | Role        | kube-system | system:controller:token-cleaner             | Fri Oct 10 08:57:58 2025 (4 days) |
| CRITICAL | ClusterRole | None        | admin                                       | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | cluster-admin                               | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | edit                                        | Fri Oct 10 08:57:57 2025 (4 days) |
| LOW      | ClusterRole | None        | system:aggregate-to-admin                   | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:aggregate-to-edit                    | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:cronjob-controller        | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:daemon-set-controller     | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:deployment-controller     | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:controller:generic-garbage-collector | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:controller:horizontal-pod-autoscaler | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:job-controller            | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:controller:namespace-controller      | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:persistent-volume-binder  | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:replicaset-controller     | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:replication-controller    | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:controller:resourcequota-controller  | Fri Oct 10 08:57:57 2025 (4 days) |
| HIGH     | ClusterRole | None        | system:controller:statefulset-controller    | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:kube-controller-manager              | Fri Oct 10 08:57:57 2025 (4 days) |
| CRITICAL | ClusterRole | None        | system:node                                 | Fri Oct 10 08:57:57 2025 (4 days) |
+----------+-------------+-------------+---------------------------------------------+-----------------------------------+