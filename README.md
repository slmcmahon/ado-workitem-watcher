About
-

This is a work in progress.  For vscode, add the following launch.json to your .vscode folder:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "ASB_CONNECTION_STRING": "",
                "ASB_QUEUE": "",
                "ADO_ORG": "",
                "ADO_PROJECT": "",
                "ADO_PAT": "",
                "ASB_POLL_INTERVAL_SECONDS": "5"
            }
        }
    ]
}
```

TODO
-
lots of error handling