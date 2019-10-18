## Ops manual

### What is it?

This is a tool developed within the Cyber Security tooling team to monitor estate-wide usage of the github security advisory service, specifically Dependabot.

#### Architecture
```
* A [Lambdas](https://aws.amazon.com/lambda/) which connect to GitHub and Splunk
```
### Where is it?

```
The staging and developer environments are hosted on the `gds-digital-security-test` (`103495720024`) AWS account.
```
#### The code

The primary codebase is [cyber-security-security-advisory-dashboard](https://github.com/alphagov/cyber-security-security-advisory-dashboard)
which contains the instructions to load an existing environment or to create a new environment from scratch.

### Is it working?

The tool dumps data to splunk once a day. If this data stream stops, it's not working. Any alerting can be based on that.
There are no more frequent health checks because this tool is not vital to day-to-day, Dependabot is.

#### Testing

There is a Concourse pipeline that runs the unit tests before deploying.

There are instructions for running the [unit tests](https://github.com/alphagov/cyber-security-security-advisory-dashboard). The unit tests do not require AWS credentials.

### How do I fix it?

There are a few places to look to figure out what's gone wrong.

#### Concourse
You can check the status of the [Concourse pipeline](https://cd.gds-reliability.engineering/teams/cybersecurity-tools/pipelines/github-security-advisories)

If it's all green it should be OK but if the unit tests
have failed or if the concourse pipeline itself has failed you should see
a non-green task. Amber/brown generally means that Concourse is still running
or has failed (it has failed in the past when another pipeline is very
resource intensive).

If something has gone wrong with our bit the task should be red. Clicking
on the red task will show the logs for the process that failed.

#### CloudWatch logs

The first place to look is CloudWatch.
Each environment consists of of a lambda.
There are multiple instances of the lambda so it can be helpful to
search CloudWatch insights for `ERROR`.

     fields @timestamp, @message
     | filter @message like "ERROR"
     | sort @timestamp desc
     | limit 20

### Where should people ask for help?

In the [#cyber-security-help](https://gds.slack.com/messages/CCMPJKFDK) slack channel.

### How should people give feedback?

Drop an issue on the repository's [github issues](https://github.com/alphagov/cyber-security-security-advisory-dashboard/issues)

### Who is responsible?

Cyber. Or YOU?

### How is it deployed?

```
It's deployed by the [shared tenancy Concourse](https://cd.gds-reliability.engineering/)
run by RE autom8.

To view the pipeline you need to login and have access to the
cybersecurity-tools space. You can request access from the
[#re-autom8](https://gds.slack.com/messages/CD1F78YJU) team.

The code to deploy the pipeline along with instructions are in the
[csw-concourse/README.md](https://github.com/alphagov/csw-concourse).

```

#### How do I delete it?

To delete an environment run a `terraform destroy`

#### How do I recreate it?

To create an environment follow the instructions in the readme.

### How does it work?

The infrastructure is terraformed from the terraform in the terraform directory.

#### The audit process

The audit process is triggered by a scheduled lambda that runs at 11pm everyday

### How are secrets managed?

Secrets are stored in [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).

The lambdas run with an [IAM execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
which grants them access to read the SSM parameters at runtime.
