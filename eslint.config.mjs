
// eslint.config.mjs
import eslint from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";

import securityNode from "eslint-plugin-security-node";               // Node.js security rules
import noUnsanitized from "eslint-plugin-no-unsanitized";             // DOM XSS prevention
import * as regexpPlugin from "eslint-plugin-regexp";                 // safer regexes

export default [

  {
    ignores: ["node_modules/", "dist/", "build/", "coverage/"],
  },

  eslint.configs.recommended, 


  regexpPlugin.configs["flat/recommended"], 


  {
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },

  {
    plugins: {
      "security-node": securityNode,
      "no-unsanitized": noUnsanitized,
    },

    rules: {
      "security-node/detect-child-process": "error",  
      "security-node/detect-eval-with-expr": "error",
      "security-node/detect-runinthiscontext-method-in-nodes-vm": "error",

      "security-node/detect-insecure-randomness": "warn",
      "security-node/detect-possible-timing-attacks": "warn",

      "security-node/detect-non-literal-require-calls": "error",

      "security-node/detect-buffer-unsafe-allocation": "error",

      "security-node/detect-dangerous-redirects": "warn",

      "security-node/detect-option-rejectunauthorized-in-nodejs-httpsrequest": "error",

      "security-node/detect-html-injection": "warn",
      "security-node/detect-nosql-injection": "warn",
      "security-node/detect-sql-injection": "warn",

      "no-unsanitized/method": "error",
      "no-unsanitized/property": "error",
    },
  },

  ...tseslint.config({
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
      },
    },
    rules: {
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  }),
];
