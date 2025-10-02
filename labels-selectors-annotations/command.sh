kubectl run nginx-1 --image=nginx -l env=dev,tier=frontend,ingress=true && \
kubectl run nginx-2 --image=nginx -l env=dev,tier=backend,ingress=false && \
kubectl run nginx-3 --image=nginx -l env=prod,tier=frontend,ingress=true && \
kubectl run nginx-4 --image=nginx -l env=prod,tier=backend,ingress=false && \
kubectl run nginx-5 --image=nginx -l env=qa,tier=db