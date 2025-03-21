import js from "@eslint/js";
import globals from "globals";
import importPlugin from "eslint-plugin-import";
import typescriptParser from "@typescript-eslint/parser";
import typescriptPlugin from "@typescript-eslint/eslint-plugin";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default tseslint.config(
    { ignores: ["./dist", "**/*config*"] },
    {
        extends: [js.configs.recommended, ...tseslint.configs.recommended],
        files: ["**/*.{ts,tsx}"],
        languageOptions: {
            ecmaVersion: 2020,
            globals: globals.browser,
        },
        languageOptions: {
            parser: typescriptParser,
        },
        linterOptions: {
            reportUnusedDisableDirectives: "warn",
            reportUnusedInlineConfigs: "warn",
        },
        plugins: {
            import: importPlugin,
            prettier: prettier,
            "react-hooks": reactHooks,
            "react-refresh": reactRefresh,
            "@typescript-eslint": typescriptPlugin,
        },
        rules: {
            ...reactHooks.configs.recommended.rules,
            ...typescriptPlugin.configs.recommended.rules,
            ...prettier.rules,
            "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
            "@typescript-eslint/ban-ts-comment": "off",
            "import/first": "off",
        },
        settings: {
            "import/resolver": {
                // You will also need to install and configure the TypeScript resolver
                // See also https://github.com/import-js/eslint-import-resolver-typescript#configuration
                typescript: true,
                node: true,
            },
        },
    },
);
