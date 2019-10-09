## Ops manual

### What is it?

This is a tool developed within the Cyber Security tooling team
to audit AWS accounts for common mis-configurations such as open
bucket policies or security groups.

#### Architecture

* A [Route53](https://aws.amazon.com/route53/) record pointing to ...
* a [CloudFront](https://aws.amazon.com/cloudfront/) CDN which routes to ...
* an [API Gateway](https://aws.amazon.com/api-gateway/) which routes to ...
* some [Lambdas](https://aws.amazon.com/lambda/) which connect to ...
* A [VPC](https://aws.amazon.com/vpc/) via an [ENI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html) which allow it to connect to ...
* A PostgreSQL [RDS](https://aws.amazon.com/rds/) instance in the VPC.

### Where is it?

There are multiple CSW environments. The resources deployed to AWS are
all prefixed with `csw-[env]`.

* Production (env=`prod`) - [https://csw.gds-cyber-security.digital](https://csw.gds-cyber-security.digital)
* Staging (env=`uat`) - [https://uat.csw.staging.gds-cyber-security.digital](https://uat.csw.staging.gds-cyber-security.digital)
* Developers (env=`[first_name]`) - Chalice deploys a default API Gateway domain without CloudFront.
  You can find your API Gateway URL in `csw-backend/environments/[env]/.chalice/deployed/[env].json`

The production environment is hosted on the `gds-digital-security` (`779799343306`) AWS account.

The staging and developer environments are hosted on the `gds-digital-security-test` (`103495720024`) AWS account.

#### The code

The primary codebase is [csw-backend](https://github.com/alphagov/csw-backend)
which contains the instructions to load an existing environment or to
create a new environment from scratch.  

### Is it working?

The primary measures of health are [Uptimerobot](https://uptimerobot.com/) checks.
These check that the interface homepage loads from API Gateway and from
the CloudFront custom domain.

    TODO - At some point we should refuse direct access to API Gateway
    At the moment it can be useful to diagnose which thing is broken.

There is a shared login which can be shared via Lastpass and failures
are automatically reported to the [#cyber-security-alerts](https://gds.slack.com/messages/GFNAH8W64)
slack channel.

There is also the beginnings of some health monitoring in Prometheus
via the [shared Grafana](https://grafana-paas.cloudapps.digital).
There is a dashboard called CSW and you have to switch orgs to the
`Cyber Security` org.

On the tool itself there is a
[statistics page](https://csw.gds-cyber-security.digital/statistics),
which has a bunch of graphs that tell you what the current status of
the audits is.    

#### Testing

There is a Concourse pipeline that runs the unit tests and end-to-end
tests but coverage is limited.

The unit tests largely test that the audit logic functions as expected.

The end-to-end tests check that the authorisation works (although they
can't test the Google OAuth authentication) and that the stats endpoints
work which in turn tests that the SQL scripts to create the stats are
working.

There are instructions for running the [unit tests](https://github.com/alphagov/csw-backend#unit-tests)
and [end-to-end tests](https://github.com/alphagov/csw-backend#end-to-end-testing).
The unit tests do not require AWS credentials but the end-to-end tests
do.

### How do I fix it?

There are a few places to look to figure out what's gone wrong.

#### Concourse
You can check the status of the [Concourse pipeline](https://cd.gds-reliability.engineering/teams/cybersecurity-tools/pipelines/csw).

If it's all green it should be OK but if the unit tests or end-to-end tests
have failed or if the concourse pipeline itself has failed you should see
a non-green task. Amber/brown generally means that Concourse is still running
or has failed (it has failed in the past when another pipeline is very
resource intensive).

If something has gone wrong with our bit the task should be red. Clicking
on the red task will show the logs for the process that failed.  

#### CloudWatch logs

The first place to look is CloudWatch.
Each environment consists of a number of lambdas.
The interface is all served by a single lambda `csw-[env]`
(`csw-prod` for the production service).
There are multiple instances of the lambda so it can be helpful to
search CloudWatch insights for `ERROR`.

     fields @timestamp, @message
     | filter @message like "ERROR"
     | sort @timestamp desc
     | limit 20

The audit and other scheduled tasks are run by individual lambdas which
match the function name linked to the `@app.lambda_function()` decorator.

The names are consistently inconsistent in that they are prefixed with
csw-[env] (kebab case) but because they're python functions the rest
of the name is snake case.

With these it's especially useful to use insights since the parallel
processing in SQS results in many concurrent lambda instances.

#### RDS

You can login to the RDS via a bastion host deployed by terraform.

    TODO - We should switch to SSM Session Manager at some point.

You'll need to retrieve the RSA key files for the env from
SSM Parameter Store and save to your local `.ssh` folder.

These are stored in `/csw/[env]/privatekey` and `/csw/[env]/publickey`
in the `eu-west-1` (Ireland) region for the relevant AWS account.

You can get the terraform outputs and credentials by running the
[environment.load task](https://github.com/alphagov/csw-backend#loading-an-existing-environment).

This should create config files in `csw-backend/environments/[env]`.

The bastion IP and RDS connection string are defined in `settings.json`.

The RDS credentials are currently in env vars in `.chalice/chalice.json`.

    TODO - These are stored in SSM and should be being retrieved from
    SSM at runtime rather than passed in as env vars in the config.

### How is access managed?

Authentication is via Google OAuth2 to our domain.

The Google OAuth credentials are managed in
[Google Cloud Console](https://console.cloud.google.com/iam-admin/iam?orgonly=true&project=cloud-security-watch&supportedpurview=organizationId)
and served up by SSM Parameter Store to the app.   

Authorisation is handled by linking users to product teams in IAM roles
built by terraform.  

A full description of how access is managed can be found in the
[csw-configuration/users/README.md](https://github.com/alphagov/csw-configuration/blob/master/users/README.md).

The access management terraform is not currently run as part of the
deploy pipeline. You need to run it from the code with appropriate
credentials (gds-cli or aws-vault).

    aws-vault exec cst-prod -- terraform init -reconfigure
    \# add terraform plan?
    aws-vault exec cst-prod -- terraform apply

### Where should people ask for help?

In the [#cyber-security-help](https://gds.slack.com/messages/CCMPJKFDK) slack channel.

### How should people give feedback?

For now as above.

    TBD - should we switch on github issues?

### Who is responsible?

We don't have an answer to this yet.

    TBD - We may need an ops team on rotation who support cyber's
    services. Alternatively we might have an interruptible for the
    dev team which kind of amounts to the same thing.

### How is it deployed?

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

#### How do I delete it?

To delete an environment follow the instructions in the
[csw-backend/README.md](https://github.com/alphagov/csw-backend#delete-and-existing-environment).

#### How do I recreate it?

To create an environment follow the instructions in the
[csw-backend/README.md](https://github.com/alphagov/csw-backend#environmentbuild).

### How does it work?

The infrastructure is terraformed
(from the [csw-infra](https://github.com/alphagov/csw-infra) repository).

Terraform is run from a gulp task in [csw-backend](https://github.com/alphagov/csw-backend)
as part of the deploy process. Terraform deploys the VPC, security groups,
subnets, routes and RDS.  

Gulp is also responsible for setting and getting parameters from SSM and
translating the terraform output (security groups, subnets and RDS connection
settings) into the Chalice `config.json` file for the `chalice deploy`
and managing all the symlinking.

[Chalice](https://chalice.readthedocs.io/en/latest/) deploys
[lambda](https://aws.amazon.com/lambda/) and
[API Gateway](https://aws.amazon.com/api-gateway/).

A second terraform deploys the DNS config (Route53) and CloudFront distribution.

    TODO - There are lots of moving parts and this would be simplified
    by converting Chalice to Flask and deploying the whole thing with
    terraform.

    We would also remove the VPC and manage access to the RDS soley
    via security groups which would remove the need for the ENIs and
    speed up lambda provisioning.

#### The audit process

The audit process is triggered by a scheduled lambda and then uses
[SQS](https://aws.amazon.com/sqs/) to parallelise the processing of
multiple checks across multiple accounts.

#### The interface

The Chalice interface is a routed app which if not extended from
[Flask](https://palletsprojects.com/p/flask/) uses similar syntax.

The interface is largely read-only with the exception of users adding
exceptions for specific check failures.

#### The API
There are a few API endpoints serving up statistics with a view to
those being built into the dashboard screens by our desks.

There is a [Prometheus](https://prometheus.io/) metrics endpoint that
serves up some health data but we're not currently monitoring the output.  

### How are secrets managed?

Secrets are stored in [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).

The lambdas run with an [IAM execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
which grants them access to read the SSM parameters at runtime.

### How is cross-account access granted?

Cross account access is granted via an IAM role defined in each target
account. The IAM role implements the standard SecurityAudit policy and
adds inline policies to grant `support:*` for Trusted Advisor as well as
`sts:GetCallerIdentity` for debugging so you can confirm the role has
been successfully assumed.

The GDSSecurityAudit role is assumable by a chain role (GDSSecurityAuditChain)
defined in the parent (billing) account.  

### What are npm and gulp used for?

Initially [npm](https://www.npmjs.com/) and [gulp](https://gulpjs.com/)
were configured to install the [govuk-frontend](https://github.com/alphagov/govuk-frontend)
and to compile the [SASS](https://sass-lang.com/) and JavaScript.

We then had a requirement to build a Chalice `config.json` file using
the outputs from [Terraform](https://www.terraform.io/) which gulp
would do relatively easily.

We then built a lot of other build tasks using gulp to run the various
processes.

These gulp tasks have been stitched together into a Concourse pipeline.

The npm `package.json` also installs the csw-infra repository and the
Terraform is configured and run from inside csw-backend.
