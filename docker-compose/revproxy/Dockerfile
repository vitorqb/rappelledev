FROM nginx:1.18.0
COPY entrypoint.sh /entrypoint.sh
COPY nginx.config /etc/nginx/nginx.conf

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--", "nginx", "-g", "daemon off;"]
