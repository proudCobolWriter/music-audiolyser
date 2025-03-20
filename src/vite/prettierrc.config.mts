// prettier.config.ts, .prettierrc.ts, prettier.config.mts, or .prettierrc.mts

import { type Config } from "prettier";

/**
 * @see https://prettier.io/docs/configuration
 **/

const config: Config = {
    trailingComma: "es5",
    useTabs: false,
    tabWidth: 4,
    semi: true,
    singleQuote: true,
};

export default config;
