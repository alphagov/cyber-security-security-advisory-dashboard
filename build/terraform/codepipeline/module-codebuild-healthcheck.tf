module "codepipeline-healthcheck" {
  source                         = "github.com/alphagov/cyber-security-shared-terraform-modules//cloudwatch/cloudwatch_report_codepipeline_status"
  pipeline_name                  = "${var.pipeline_name}"
  health_notification_topic_name = "cloudwatch_event_forwarder"
}