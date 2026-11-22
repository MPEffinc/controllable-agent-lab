import unittest

from scripts.progent_docker_backend import DockerBackend, DockerBackendError


class OwnershipTest(unittest.TestCase):
    def test_unknown_resource_never_reaches_docker(self):
        backend = DockerBackend("unit")
        with self.assertRaises(DockerBackendError):
            backend.stop("sregym-lab-worker")
        self.assertEqual(backend.invocations, [])


if __name__ == "__main__":
    unittest.main()
