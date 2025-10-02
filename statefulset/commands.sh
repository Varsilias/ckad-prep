kubectl run -i --tty dns-test --rm --image=busybox:1.28 --restart=Never
kubectl run -i --tty test-pod --rm --image=nginx:alpine --restart=Never -- sh

curl flask-normal

curl flask-headless

nslookup flask-normal
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      flask-normal
Address 1: 10.103.188.108 flask-normal.default.svc.cluster.local


 nslookup flask-headless
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      flask-headless
Address 1: 10.244.0.8
Address 2: 10.244.1.15
Address 3: 10.244.1.16

