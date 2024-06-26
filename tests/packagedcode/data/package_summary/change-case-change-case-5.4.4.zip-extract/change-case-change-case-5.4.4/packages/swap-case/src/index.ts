export function swapCase(input: string, locale?: string[] | string) {
  let result = "";
  for (const char of input) {
    const lower = char.toLocaleLowerCase(locale);
    result += char === lower ? char.toLocaleUpperCase(locale) : lower;
  }
  return result;
}
