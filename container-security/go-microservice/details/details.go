package details

import "os"

func GetHostname() (string, error) {
	return os.Getenv("HOSTNAME"), nil
}

func GetIP() (string, error) {
	return os.Getenv("KUBERNETES_SERVICE_HOST"), nil
}
