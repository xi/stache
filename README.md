Yet another [mustache](http://mustache.github.io/mustache.5.html) implementation.

# Usage

```python
import stache
from html import escape

template = stache.get_template('foo.html')
html = stache.render(template, {'title': 'my first website'}, escape)

template = stache.parse('{{#foo}}{{bar}}{{/foo}}')
output = stache.render(template, {'foo': True, 'bar': 'Hello world!'}, lambda x: x)
```

# Supported features

-	variables: `{{foo}}`
-	safe variables: `{{&foo}}`
-	sections: `{{#foo}}{{bar}}{{/foo}}`
-	inverted sections: `{{^foo}}{{bar}}{{/foo}}`
-	partials: `{{>path/to/file.html}}`
-	comments: `{{! ignore me }}`
-	lambdas:

	```python
	def highlight(nodes, context, escape):
		text = stache.render(nodes, context, lambda x: x)
		return pygments.highlight(text)

	template = stache.parse('{{#highlight}}{{code}}{{/highlight}}')
	output = stache.render(template, {'code': …, 'highlight': highlight}, escape)
	```
-	`.` to access the current context object: `{{.}}`
-	missing variables are treated as empty strings/falsy
-	context inheritance: you can access variables from the outer contexts (unless they are shadowed)
-	lines with standalone template tags are removed from the output

# Not supported

-	changing delimiters
-	`.` to go down the context hierarchy: `{{foo.bar}}`
-	`{{{foo}}}` for safe variables (use `{{&foo}}` instead)
-	multi line comments
-	partials are not indented
