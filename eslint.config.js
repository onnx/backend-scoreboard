import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      globals: {
        ...globals.browser,
        Chart: "writable",
        palette: "writable",
      },
    },
    rules: {
      "no-new": "warn",
      "no-undef": "warn",
      "no-unused-vars": "warn",
      semi: ["warn", "always"],
    },
  },
];
