# Title Case

> Transform a string into [title case](https://en.wikipedia.org/wiki/Letter_case#Title_case) following English rules.

## Installation

```
npm install title-case --save
```

## Usage

```js
import { titleCase } from "title-case";

titleCase("string"); //=> "String"
titleCase("follow step-by-step instructions"); //=> "Follow Step-by-Step Instructions"
```

### Options

- `locale?: string | string[]` Locale used for `toLocaleUpperCase` during case transformation (default: `undefined`)
- `sentenceCase?: boolean` Only capitalize the first word of each sentence (default: `false`)
- `sentenceTerminators?: Set<string>` Set of characters to consider a new sentence under sentence case behavior (e.g. `.`, default: `SENTENCE_TERMINATORS`)
- `smallWords?: Set<string>` Set of words to keep lower-case when `sentenceCase === false` (default: `SMALL_WORDS`)
- `titleTerminators?: Set<string>` Set of characters to consider a new sentence under title case behavior (e.g. `:`, default: `TITLE_TERMINATORS`)
- `wordSeparators?: Set<string>` Set of characters to consider a new word for capitalization, such as hyphenation (default: `WORD_SEPARATORS`)

## TypeScript and ESM

This package is a [pure ESM package](https://gist.github.com/sindresorhus/a39789f98801d908bbc7ff3ecc99d99c) and ships with TypeScript definitions. It cannot be `require`'d or used with CommonJS module resolution in TypeScript.

## License

MIT
