workflow "New workflow" {
  resolves = ["Publish Python Package"]
  on = "push"
}

action "Publish Python Package" {
  uses = "mariamrf/py-package-publish-action@v0.0.2"
  secrets = ["TWINE_USERNAME", "TWINE_PASSWORD"]
  env = {
    PYTHON_VERSION = "3.7.0"
  }
}
