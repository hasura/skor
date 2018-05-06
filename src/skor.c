/* skor.c

   Waits for changes in the database and forwards them to
   a webhook

   Usage as shown in usageError().
*/
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <libpq-fe.h>  /* libpq */
#include <curl/curl.h> /* libcurl to send requests */
#include "req.c"

/* closes the connection and exits */
static void clean_exit(PGconn *conn) {
    PQfinish(conn);
    exit(EXIT_FAILURE);
}

static void help_msg(const char *prog_name) {
    fprintf(stderr, "usage: %s <dsn of db> <webhook-url> [log_level(0-5)]\n", prog_name);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    /* default level INFO or greater */
    int log_level = 2;
    PGconn     *conn;
    PGresult   *res;
    PGnotify   *notify;

    /* Check the arguments */
    if (argc < 3 || argc > 4 || strcmp(argv[1], "--help") == 0)
        help_msg(argv[0]);

    if (argc == 4)
        log_level = atoi(argv[3]);

    log_set_quiet(1);
    log_set_level(log_level);
    log_set_fp(stdout);


    /* Establish a connection to the postgres database */
    conn = PQconnectdb(argv[1]);

    /* Check to see that the backend connection was successfully made */
    if (PQstatus(conn) != CONNECTION_OK) {
        log_fatal("connection to database failed: %s",
                  PQerrorMessage(conn));
        clean_exit(conn);
    }

    log_info("listening for notifications from postgres");

    /* Issue LISTEN command to enable notifications from the rule's NOTIFY. */
    res = PQexec(conn, "LISTEN skor");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        log_fatal("LISTEN command failed: %s", PQerrorMessage(conn));
        PQclear(res);
        clean_exit(conn);
    }
    /* Avoid leaks */
    PQclear(res);

    /* Listen to notifications */
    while (1)
    {
        /* Sleep until something happens on the connection. */
        int         sock;
        fd_set      input_mask;

        sock = PQsocket(conn);

        if (sock < 0)
            break;              /* shouldn't happen */

        FD_ZERO(&input_mask);
        FD_SET(sock, &input_mask);

        log_debug("waiting for data on socket");
        fflush(stdout);
        if (select(sock + 1, &input_mask, NULL, NULL, NULL) < 0) {
            log_fatal("select() failed: %s", strerror(errno));
            clean_exit(conn);
        }

        /* Now check for input */
        PQconsumeInput(conn);
        while ((notify = PQnotifies(conn)) != NULL) {
            log_info("received notification : '%s'", notify->extra);
            if (call_webhook(argv[2], notify->extra) != 0)
                log_error("failed to send notification to the webhook");
            else
              log_info("notification sent");
            PQfreemem(notify);
        }
    }

    log_fatal("connection lost; probably the server exited?");

    /* close the connection to the database and cleanup */
    PQfinish(conn);

    exit(EXIT_FAILURE);
}
