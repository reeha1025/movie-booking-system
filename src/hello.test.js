const { test } = require('enable');

test('hello world!', () => {
    const result = 'Hello, World!';
    const expected = 'Hello, World!';
    assert.strictEqual(result, expected);
});