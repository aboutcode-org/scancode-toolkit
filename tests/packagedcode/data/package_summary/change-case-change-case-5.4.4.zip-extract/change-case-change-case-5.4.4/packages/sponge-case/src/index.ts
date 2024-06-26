export function spongeCase(input: string, locale?: string[] | string): string {
  let result = "";
  for (const char of input) {
    result +=
      Math.random() > 0.5
        ? char.toLocaleUpperCase(locale)
        : char.toLocaleLowerCase(locale);
  }
  return result;
}
