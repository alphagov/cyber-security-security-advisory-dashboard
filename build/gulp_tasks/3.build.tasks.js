/**
    Wrapper tasks to group common build and deploy functions.
 */
const gulp = require("gulp");

gulp.task(
  "assets",
  gulp.series("copy.assets", "sass.gov", "concat.js")
);
