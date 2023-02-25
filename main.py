"""
Reading files from git
"""
import io
import os
import stat
import tempfile

from git.repo.base import Repo


def _make_key_file(key: str):
    result = io.StringIO()
    result.write("-----BEGIN OPENSSH PRIVATE KEY-----\n")
    result.write(key)
    result.write("\n-----END OPENSSH PRIVATE KEY-----\n")
    return result.getvalue()


def read_git_file(key: str, repo: str, file: str) -> str:
    with tempfile.NamedTemporaryFile() as ssh_file:
        ssh_file.write(_make_key_file(key).encode("utf-8"))
        ssh_file.flush()
        os.chmod(ssh_file.name, stat.S_IRUSR)

        with tempfile.TemporaryDirectory() as tempdir:
            Repo.clone_from(
                repo,
                tempdir,
                depth=1,
                single_branch=True,
                branch="master",
                env={
                    "GIT_SSH_COMMAND": (
                        f"ssh -i {ssh_file.name} -v -o StrictHostKeyChecking=no"
                    )
                },
            )

            local_file_path = os.path.join(tempdir, file)

            with open(local_file_path, "r", encoding="utf-8") as file_read:
                return file_read.read()
