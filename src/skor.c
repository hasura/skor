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
    fprintf(stderr, "FATAL : Usage: %s <dsn of db> <webhook-url> [debug(0/1)]\n", prog_name);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    /* const char *conninfo; */
    int debug = 0;
    PGconn     *conn;
    PGresult   *res;
    PGnotify   *notify;

    /* Check the arguments */
    if (argc < 3 || argc > 4 || strcmp(argv[1], "--help") == 0)
        help_msg(argv[0]);

    if (argc == 4)
        debug = atoi(argv[3]);

    /* Establish a connection to the postgres database */
    conn = PQconnectdb(argv[1]);

    /* Check to see that the backend connection was successfully made */
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "FATAL : Connection to database failed: %s\n",
                PQerrorMessage(conn));
        clean_exit(conn);
    }

    /* Issue LISTEN command to enable notifications from the rule's NOTIFY. */
    res = PQexec(conn, "LISTEN skor");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        fprintf(stderr, "FATAL : LISTEN command failed: %s\n", PQerrorMessage(conn));
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

        fprintf(stdout, "INFO : Waiting for notifications from postgres\n");
        fflush(stdout);
        if (select(sock + 1, &input_mask, NULL, NULL, NULL) < 0) {
            fprintf(stderr, "FATAL : select() failed: %s\n", strerror(errno));
            clean_exit(conn);
        }

        /* Now check for input */
        PQconsumeInput(conn);
        while ((notify = PQnotifies(conn)) != NULL) {
            fprintf(stdout, "INFO : Received notification : '%s'\n", notify->extra);
            if (call_webhook(argv[2], notify->extra, debug) != 0)
                fprintf(stderr, "ERROR : Failed to forward notification to the webhook\n");
            else
              fprintf(stdout, "INFO : Notification sent\n");
            PQfreemem(notify);
        }
    }

    fprintf(stderr, "FATAL : Exiting! Probably the server exited?\n");

    /* close the connection to the database and cleanup */
    PQfinish(conn);

    exit(EXIT_FAILURE);
}
