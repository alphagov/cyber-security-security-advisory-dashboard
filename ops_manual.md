## Ops manual

### What is it?

This is a tool developed within the Cyber Security tooling team to monitor estate-wide usage of the github security advisory service, specifically Dependabot.

#### Architecture
> TODO
```
* A [Route53](https://aws.amazon.com/route53/) record pointing to ...
* a [CloudFront](https://aws.amazon.com/cloudfront/) CDN which routes to ...
* an [API Gateway](https://aws.amazon.com/api-gateway/) which routes to ...
* some [Lambdas](https://aws.amazon.com/lambda/) which connect to ...
* A [VPC](https://aws.amazon.com/vpc/) via an [ENI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html) which allow it to connect to ...
* A PostgreSQL [RDS](https://aws.amazon.com/rds/) instance in the VPC.
```
### Where is it?

> TODO

```
There are multiple CSW environments. The resources deployed to AWS are
all prefixed with `csw-[env]`.

* Production (env=`prod`) - [https://csw.gds-cyber-security.digital](https://csw.gds-cyber-security.digital)
* Staging (env=`uat`) - [https://uat.csw.staging.gds-cyber-security.digital](https://uat.csw.staging.gds-cyber-security.digital)
* Developers (env=`[first_name]`) - Chalice deploys a default API Gateway domain without CloudFront.
  You can find your API Gateway URL in `csw-backend/environments/[env]/.chalice/deployed/[env].json`

The production environment is hosted on the `gds-digital-security` (`779799343306`) AWS account.

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
You can check the status of the [TODO Concourse pipeline](https://cd.gds-reliability.engineering/teams/cybersecurity-tools/pipelines/TBD).

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

> TODO

```
It's deployed by the [shared tenancy Concourse](https://cd.gds-reliability.engineering/)
run by RE autom8.

To view the pipeline you need to login and have access to the
cybersecurity-tools space. You can request access from the
[#re-autom8](https://gds.slack.com/messages/CD1F78YJU) team.

Our pipeline is
[/teams/cybersecurity-tools/pipelines/csw](https://cd.gds-reliability.engineering/teams/cybersecurity-tools/pipelines/csw).

The code to deploy the pipeline along with instructions are in the
[csw-concourse/README.md](https://github.com/alphagov/csw-concourse).

There are build destroy tasks defined in Concourse but to prevent
escalation of privilege risks we have not granted the Concourse role
the permissions required to create and destroy AWS resources
(only update them).

This means that some tasks have to be run outside Concourse manually.
```

#### How do I delete it?

To delete an environment follow the instructions in the
[csw-backend/README.md](https://github.com/alphagov/csw-backend#delete-and-existing-environment).

#### How do I recreate it?

To create an environment follow the instructions in the readme.

### How does it work?

The infrastructure is terraformed
(from the [csw-infra](https://github.com/alphagov/csw-infra) repository).

As part of the ci process. Terraform deploys the VPC, security groups,
subnets, routes etc. Merge your PR and it will be done.

#### The audit process

The audit process is triggered by a scheduled lambda and then uses
[SQS](https://aws.amazon.com/sqs/) to parallelise the processing of
multiple checks across multiple accounts.

### How are secrets managed?

Secrets are stored in [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).

The lambdas run with an [IAM execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
which grants them access to read the SSM parameters at runtime.
