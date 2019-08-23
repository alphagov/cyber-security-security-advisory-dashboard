/**
    Compile the default govuk-frontend SASS and
    any extensions added by CSW and save
    compiled CSS to deployed chalicelib folder
 */
var gulp = require("gulp");
var sass = require("gulp-sass");

gulp.task("sass.gov", function() {
  return gulp
    .src("node_modules/govuk-frontend/govuk/*.scss")
    .pipe(sass().on("error", sass.logError))
    .pipe(gulp.dest("../static"));
});
