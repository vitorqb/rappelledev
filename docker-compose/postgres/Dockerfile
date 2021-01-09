FROM postgres:13.1

COPY ./rappelle-entrypoint.sh /usr/local/bin/rappelle-entrypoint.sh
RUN chmod +x /usr/local/bin/rappelle-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/rappelle-entrypoint.sh"]
CMD ["postgres"]
