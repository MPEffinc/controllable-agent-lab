import unittest
from unittest.mock import patch

from scripts.progent_docker_backend import DockerBackend, DockerBackendError


class OwnershipTest(unittest.TestCase):
    def test_runtime_is_restricted_and_kata_creation_is_bounded(self):
        with self.assertRaises(ValueError):
            DockerBackend("unit", runtime="arbitrary")
        backend = DockerBackend("unit", runtime="kata")
        with patch.object(backend, "_docker", return_value="container-id") as docker:
            with patch.object(backend, "_check_owned", return_value={}):
                backend.create("01")
        args = docker.call_args.args
        self.assertEqual(args[args.index("--runtime") + 1], "kata")
        self.assertEqual(args[args.index("--memory") + 1], "1g")
        self.assertEqual(args[args.index("--network") + 1], "none")

    def test_owned_container_cannot_switch_runtime(self):
        backend = DockerBackend("unit", runtime="kata")
        name = "cclab-progent-exp-unit-01"
        backend.owned[name] = "container-id"
        info = {"Id": "container-id", "Name": "/" + name,
                "Config": {"Labels": {"org.cclab.progent.experiment": "unit"}},
                "HostConfig": {"Runtime": "runc"}}
        with patch.object(backend, "_inspect", return_value=info):
            with self.assertRaises(DockerBackendError):
                backend.status(name)

    def test_unknown_resource_never_reaches_docker(self):
        backend = DockerBackend("unit")
        with self.assertRaises(DockerBackendError):
            backend.stop("sregym-lab-worker")
        self.assertEqual(backend.invocations, [])


if __name__ == "__main__":
    unittest.main()
