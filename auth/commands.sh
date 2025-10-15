openssl genrsa -out daniel.key 2048 # generate private key and store in file named daniel.key
openssl req -new -key daniel.key -out daniel.csr -subj "/CN=daniel/O=platform" # create a Certificate Signing Request for user "Daniel" in group "Platform"
cat daniel.csr | base64 | tr -d "\n" # convert to base64 and strip off all new line character
## Create CSR Object and apply
k apply -f csr.yaml
k get csr
NAME     AGE   SIGNERNAME                            REQUESTOR       REQUESTEDDURATION   CONDITION
daniel   6s    kubernetes.io/kube-apiserver-client   minikube-user   24h                 Pending

k certificate approve <csr-name> # approve csr name
NAME     AGE     SIGNERNAME                            REQUESTOR       REQUESTEDDURATION   CONDITION
daniel   2m49s   kubernetes.io/kube-apiserver-client   minikube-user   24h                 Approved,Issued
k certificate deny <csr-name> # approve csr name

## get the client certificate signed by the k8s cluster
k get csr daniel -o jsonpath='{.status.certificate}'

## decode the client certification
k get csr daniel -o jsonpath='{.status.certificate}' | base64 -d > daniel.crt

## send api request to api server using curl by passing all the necessary certificate and key
curl --key daniel.key --cert daniel.crt --cacert minikube1-ca.crt https://127.0.0.1:32771/version
{
  "major": "1",
  "minor": "33",
  "emulationMajor": "1",
  "emulationMinor": "33",
  "minCompatibilityMajor": "1",
  "minCompatibilityMinor": "32",
  "gitVersion": "v1.33.1",
  "gitCommit": "8adc0f041b8e7ad1d30e29cc59c6ae7a15e19828",
  "gitTreeState": "clean",
  "buildDate": "2025-05-15T08:19:08Z",
  "goVersion": "go1.24.2",
  "compiler": "gc",
  "platform": "linux/arm64"
}
k get po -v=7 # set verbose level to 7 when getting resource
I1010 11:30:47.368232   58390 loader.go:402] Config loaded from file:  /Users/danielokoronkwo/.kube/config
I1010 11:30:47.374313   58390 cert_rotation.go:141] "Starting client certificate rotation controller" logger="tls-transport-cache"
I1010 11:30:47.374831   58390 envvar.go:172] "Feature gate default state" feature="ClientsAllowCBOR" enabled=false
I1010 11:30:47.374837   58390 envvar.go:172] "Feature gate default state" feature="ClientsPreferCBOR" enabled=false
I1010 11:30:47.374840   58390 envvar.go:172] "Feature gate default state" feature="InformerResourceVersion" enabled=false
I1010 11:30:47.374842   58390 envvar.go:172] "Feature gate default state" feature="InOrderInformers" enabled=true
I1010 11:30:47.374844   58390 envvar.go:172] "Feature gate default state" feature="WatchListClient" enabled=false
I1010 11:30:47.381087   58390 round_trippers.go:527] "Request" verb="GET" url="https://127.0.0.1:32771/api/v1/namespaces/default/pods?limit=500" headers=<
	Accept: application/json;as=Table;v=v1;g=meta.k8s.io,application/json;as=Table;v=v1beta1;g=meta.k8s.io,application/json
	User-Agent: kubectl/v1.33.3 (darwin/arm64) kubernetes/80779bd
 >
I1010 11:30:47.404336   58390 round_trippers.go:632] "Response" status="200 OK" milliseconds=23
No resources found in default namespace.

#### Update KubeConfig with new set of credentials
kubectl config set-credentials daniel --client-key=daniel.key --client-certificate=daniel.crt  --embed-certs=true # create new user entry in kube config file
k config set-context daniel --cluster=minikube --user=daniel --namespace=default # create context entry for the new user

###### Permissions Check
k auth can-i list po
k auth can-i list svc


#####################################################
## SERVICE ACCOUNT TOKEN AUTHENTICATION            ##
######################################################

k create sa test
k get sa test -o yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
  creationTimestamp: "2025-10-11T09:18:25Z"
  generation: 1
  labels:
    app: nginx
  name: nginx
  namespace: default
  resourceVersion: "17169"
  uid: 3d694732-3f99-4fdf-8d94-f37c984a8f85
spec:
  containers:
  - image: nginx:1.14.2
    imagePullPolicy: IfNotPresent
    name: nginx
    ports:
    - containerPort: 80
      protocol: TCP
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-n6l58
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  nodeName: minikube-m02
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: build-robot
  serviceAccountName: build-robot
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute



  https://127.0.0.1:32781/api/v1/namespaces/default/pods?limit=500
  https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods

  curl --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt --header "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"  https://kubernetes.default.svc.cluster.local/api/v1/namespaces/$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)/pods
  curl --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt --header "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"  https://kubernetes.default.svc.cluster.local/api