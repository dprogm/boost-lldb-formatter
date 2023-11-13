You can use the formatters by running the following command from within an lldb session:

```bash
command script import path/to/data_formatters.py
```

This script currently supports the following boost types:
* `boost::variant`
* `boost::optional`
* `boost::container::small_vector`