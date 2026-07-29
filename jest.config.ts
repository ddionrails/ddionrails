import type {Config} from "@jest/types";


const config: Config.InitialOptions = {
  transform: {
    "^.+\\.ts?$": ["ts-jest",
      {
        tsconfig: {
          "outDir": "./dist/",
          "noImplicitAny": true,
          "module": "es6",
          "target": "es2017",
          "jsx": "react",
          "allowJs": true,
          "moduleResolution": "node",
        },
      },

    ],
  },
  testEnvironment: "jsdom",
  testRegex: "./assets/js/tests/.*\\_(test|spec)?\\.(ts|tsx)$",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  setupFiles: ["./assets/js/tests/mock.ts"],
  testPathIgnorePatterns: [
    "./assets/js/tests/statistics_navigation_utils_test.ts",
  ],
};

export default config;
