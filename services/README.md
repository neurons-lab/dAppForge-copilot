## Service Management
The FastAPI and Gradio demo applications run as services on the instance. Configuration files are available in the GitHub repository as `fastapi.service` and `gradio-app.service`.

If anything needs to be changed it can be done via the following command:
```bash
sudo nano /etc/systemd/system/fastapi.service or sudo nano /etc/systemd/system/gradio-app.service.
```
For modifications, use:
```bash
sudo nano /etc/systemd/system/fastapi.service
sudo nano /etc/systemd/system/gradio-app.service
```
Reload and start the services with:

```bash
sudo systemctl daemon-reload
sudo systemctl start tabby.service
sudo systemctl start streamlit.service
```