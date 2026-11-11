/* Portable Python runner: py launcher on Windows, python3 on CI/Linux. */
"use strict";
const { spawnSync } = require("node:child_process");
const candidates = process.platform === "win32"
  ? [["py", ["-3.10"]], ["python", []], ["python3", []]]
  : [["python3", []], ["python", []]];
const args = process.argv.slice(2);
for (const [binary, prefix] of candidates) {
  const result = spawnSync(binary, [...prefix, ...args], {
    stdio: "inherit",
    env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
  });
  if (result.error?.code === "ENOENT") continue;
  process.exit(result.status ?? 1);
}
console.error("Python 3 is required to build or test this portfolio.");
process.exit(1);
