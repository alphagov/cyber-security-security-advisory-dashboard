/**
    Copy the relevant parts of the govuk-frontend codebase into the deployed
    chalicelib directory
 */
const gulp = require("gulp");
const concat = require("gulp-concat");

gulp.task("copy.assets_files", function() {
  // place code for your default task here
  return gulp
    .src(["node_modules/govuk-frontend/govuk/assets/**"])
    .pipe(gulp.dest("../static"));
});

gulp.task("copy.assets_scripts", function() {
  return gulp
    .src(["node_modules/govuk-frontend/govuk/*.js"])
    .pipe(gulp.dest("../static"));
});

gulp.task("concat.js", function() {
  return gulp
    .src([
      "./node_modules/d3/dist/d3.min.js",
      "./node_modules/c3/c3.min.js",
      "./node_modules/vue/dist/vue.js",
      "./node_modules/pe-charts/lib/js/table-chart.js",
      "./node_modules/govuk-frontend/govuk/all.js",
      "./node_modules/pe-charts/lib/js/app.js"
    ])
    .pipe(concat("dist.body.js"))
    .pipe(gulp.dest("../static"));
});

gulp.task(
  "copy.assets",
  gulp.series("copy.assets_files", "copy.assets_scripts")
);
