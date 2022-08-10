# burendo-repo-template-terraform
This repo contains Makefile to fit the standard pattern. This repo is a base to create new Terraform repos, adding the githooks submodule, making the repo ready for use.  After cloning this repo, please run: make bootstrap

## Usage

### First run
`pip3 install -r requirements.txt`

### Bootstrap

Replace any mentions of `example` with the name of your new repository, e.g. `burendo-my-service`

Create your AWS session with the cli, and assume the `Administrator` role. For this I personally use [awsume](https://awsu.me/).

then:

`make bootstrap`
`terraform init`
