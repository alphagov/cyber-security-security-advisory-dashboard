const gulp = require("gulp");
const reqDir = require("require-dir"),
  tasks = reqDir("gulp_tasks/");

gulp.task("default", gulp.series("assets"));
