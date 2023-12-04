# How to set up SSL
`conda config --remove-key ssl_verify` to reset to default to avoid different behaviours.
`conda config --set ssl_verify true` to reset the ssl
`conda config --show ssl_verify` to show the ssl_verify file
`conda config --set ssl_verify "C:\\Users\\nq9093\\Downloads\\conda.crt"` to activate the system to use this `conda.crt` file instead!
`conda update conda` to test if certificates are installed properly
`conda update certifi` to update the certificates
`conda create --name=test python=3.12` is a better way to creating the environment as windows does not automatically fill the rest to make it incomplete.

`conda config --set proxy_servers.http http://www-proxy.sandvik.com:8080` to update the proxy server address.

`conda config --set proxy_servers.https http://www-proxy.sandvik.com:8080` to update https proxy server address.

`git config (--global) http.sslCAInfo "C:\\Users\\nq9093\\Downloads\\conda.crt"` to set up git to use ssl certificate on the global level! Remove `--global` to make it local repo sepcific.

# Common code to be used to generate mp4 from png files
`ffmpeg -framerate 50 -i P_%03d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4` -> No GPU acceleration
`ffmpeg -framerate 50 -i P_%03d.png -c:v h264_nvenc -profile:v high -cq 20 -pix_fmt yuv420p output.mp4` -> GPU acceleration
