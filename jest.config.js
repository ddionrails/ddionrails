module.exports = {
  transform: {"^.+\\.ts?$": "ts-jest"},
  testEnvironment: "jsdom",
  testRegex: "./assets/js/tests/.*\\_(test|spec)?\\.(ts|tsx)$",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  setupFiles: ["./assets/js/tests/mock.ts"],
};
