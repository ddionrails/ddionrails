const config = {
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
    "^.+\\.js$": ["ts-jest",
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
  transformIgnorePatterns: [
    "node_modules/(?!(@faker-js)/)",
  ],
  testEnvironment: "jsdom",
  testRegex: "./assets/js/tests/.*\\.(test|spec)\\.(ts|tsx)$",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  setupFiles: ["./assets/js/tests/mock.ts"],
  testPathIgnorePatterns: [
    "./assets/js/tests/statistics_navigation_utils.test.ts",
  ],
};

module.exports = config;
