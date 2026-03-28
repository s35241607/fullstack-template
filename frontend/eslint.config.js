import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import tsParser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import globals from 'globals'

export default [
  js.configs.recommended,

  // TypeScript-only files
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tsParser,
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },

  // Vue files — eslint-plugin-vue v10 flat config (includes Vue parser)
  ...pluginVue.configs['flat/recommended'],

  // Overrides for .vue files (add TS parser inside <script>)
  {
    files: ['**/*.vue'],
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
      parserOptions: {
        parser: tsParser,
      },
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      // Project-specific overrides
      'vue/multi-word-component-names': 'off',
      'vue/block-lang': ['error', { script: { lang: 'ts' } }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      // Disable overly strict formatting rules (Prettier handles this)
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      'vue/attributes-order': 'off',
      'vue/require-default-prop': 'off',
    },
  },

  {
    ignores: ['dist/**', 'node_modules/**', '*.config.js'],
  },
]
