## fifo
This is a python implementation of (most) of the Project FiFo API along with a console client to access it.

## Examples

### Total memory in cloud

```bash
fifo hypervisors list --fmt free,used,reserved -H | sed 's/MB//g' | awk  '{total+=($1 + $2 + $3)} END{print total}'
```
