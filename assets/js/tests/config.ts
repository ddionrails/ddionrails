
import type {JestConfigWithTsJest} from "ts-jest";

const jestConfig: JestConfigWithTsJest = {
  // [...]
  transform: {
    // '^.+\\.[tj]sx?$' to process js/ts with `ts-jest`
    // '^.+\\.m?[tj]sx?$' to process js/ts/mjs/mts with `ts-jest`
    "^.+\\.tsx?$": [
      "ts-jest",
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
};

export default jestConfig;
