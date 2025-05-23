#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "rep.h"
#include "move_map.h"

/* Forward declarations */
int offset_to_id(int offset_x, int offset_y, int promo);
void id_to_offset(int unique_id, int* offset_x, int *offset_y, int *promo);
int index_to_offset_id(int index);
int offset_id_to_index(int offset_id);
int move_str_to_rep_int(char *move_str);

/* Converts the standard vector legal mask int a move array specific mask, used
 * for transformers.
 */
void legal_mask_to_move_arr_mask(int *move_arr_mask, int *legal_mask, int N) {

#pragma omp parallel for
    for (size_t i = 0; i < (size_t)N; i++) {
        int idx = 0;
        for (size_t j = 0; j < (64 * OFF_TOTAL); j++) {
            if (legal_mask[i * 64 * OFF_TOTAL + j] == 1) {

                int move_arr[5];
                int_to_move_arr(move_arr, (int*)&j);

                int move_rep[2] = {5, 9};
                move_arr_to_move_rep(move_rep, move_arr);

                move_arr_mask[i * 2 * 256 + idx] = move_rep[0];
                move_arr_mask[i * 2 * 256 + idx + 1] = move_rep[1];

                idx += 2;
            }
        }
    }
}

/* Converts a move array into the move rep format for transformers. */
void move_arr_to_move_rep(int *move_rep, int *move_arr) {

    char move_str[6];
    array_to_move_str(move_str, move_arr);

    char sub_move[4];
    sub_move[0] = move_str[0];
    sub_move[1] = move_str[1];
    sub_move[2] = '\0';

    move_rep[0] = move_str_to_rep_int(sub_move);

    sub_move[0] = move_str[2];
    sub_move[1] = move_str[3];
    if (move_str[4] == ' ') {
        sub_move[2] = '\0';
    } else {
        sub_move[2] = move_str[4];
        sub_move[3] = '\0';
    }

    move_rep[1] = move_str_to_rep_int(sub_move);
}

/* Converts an integer move id into an actual move type. */
void int_to_move(Move *move, int move_int) {
    int move_arr[5];
    int_to_move_arr(move_arr, &move_int);
    array_to_move(move, move_arr);
}

/* Converts a move type into an integer move id. */
void move_to_int(int* move_int, Move move) {
    int move_arr[6];
    move_to_array(move_arr, move);
    move_arr_to_int(move_int, move_arr);
}

/* Converts a move array into an integer move id. */
void move_arr_to_int(int *move_int, int*move_arr) {
    int offset_x = move_arr[0]  - move_arr[2];
    int offset_y = move_arr[1]  - move_arr[3];
    int promo = move_arr[4];
    int offset_index = offset_id_to_index(offset_to_id(offset_x, offset_y, promo));
    *move_int = ((8 * move_arr[0] + move_arr[1]) * OFF_TOTAL) + offset_index;
}

/* Converts an integer move id into a move array. */
void int_to_move_arr(int *move_arr, int *move_int_arr) {
    // Using a similar algorithm to OpenSpiel, see:
    // https://github.com/deepmind/open_spiel/blob/4cd1e5889e447d285eb3f16901ccab5c14e62187/open_spiel/games/chess.cc#L162
    int move_int = move_int_arr[0];
    int start_pos = (int) floor(move_int / OFF_TOTAL);

    move_arr[0] = (int) floor(start_pos / 8);
    move_arr[1] = start_pos - move_arr[0] * 8;

    int offset_index = move_int - (start_pos * OFF_TOTAL);
    int offset_id = index_to_offset_id(offset_index);

    int offset_x;
    int offset_y;
    int promo;

    id_to_offset(offset_id, &offset_x, &offset_y, &promo);
    move_arr[2] = move_arr[0] - offset_x;
    move_arr[3] = move_arr[1] - offset_y;
    move_arr[4] = promo;
}

int offset_to_id(int offset_x, int offset_y, int promo) {
    return 10000 * offset_x + (offset_y + 8) * 100 + promo;
}

void id_to_offset(int unique_id, int* offset_x, int *offset_y, int *promo) {
    int ox;
    if (unique_id < 0) {
        ox = -1 * (int) ceil((float)abs(unique_id) / 10000);
    } else {
        ox = (int) floor((float)unique_id / 10000);
    }
    int oy = (int) floor(((float) unique_id - ox * 10000) / 100);
    int p = unique_id - (ox * 10000 + oy * 100);

    *offset_x = ox;
    *offset_y = oy - 8;
    *promo = p;
}

/** Machine Generated code, used to from the unique move id/index to the offset id */
int index_to_offset_id(int index) {
    int out = 0;
    switch(index) {
        case 0: out = -69200; break;
        case 1: out = 100; break;
        case 2: out = -69900; break;
        case 3: out = -68500; break;
        case 4: out = -59200; break;
        case 5: out = 200; break;
        case 6: out = -59800; break;
        case 7: out = -58600; break;
        case 8: out = -49200; break;
        case 9: out = 300; break;
        case 10: out = -49700; break;
        case 11: out = -48700; break;
        case 12: out = -39200; break;
        case 13: out = 400; break;
        case 14: out = -39600; break;
        case 15: out = -38800; break;
        case 16: out = -29200; break;
        case 17: out = 500; break;
        case 18: out = -29500; break;
        case 19: out = -28900; break;
        case 20: out = -19200; break;
        case 21: out = 600; break;
        case 22: out = -19400; break;
        case 23: out = -19000; break;
        case 24: out = -9200; break;
        case 25: out = 700; break;
        case 26: out = -9300; break;
        case 27: out = -9100; break;
        case 28: out = 10800; break;
        case 29: out = 900; break;
        case 30: out = 10900; break;
        case 31: out = 10700; break;
        case 32: out = 20800; break;
        case 33: out = 1000; break;
        case 34: out = 21000; break;
        case 35: out = 20600; break;
        case 36: out = 30800; break;
        case 37: out = 1100; break;
        case 38: out = 31100; break;
        case 39: out = 30500; break;
        case 40: out = 40800; break;
        case 41: out = 1200; break;
        case 42: out = 41200; break;
        case 43: out = 40400; break;
        case 44: out = 50800; break;
        case 45: out = 1300; break;
        case 46: out = 51300; break;
        case 47: out = 50300; break;
        case 48: out = 60800; break;
        case 49: out = 1400; break;
        case 50: out = 61400; break;
        case 51: out = 60200; break;
        case 52: out = 70800; break;
        case 53: out = 1500; break;
        case 54: out = 71500; break;
        case 55: out = 70100; break;
        case 56: out = 20900; break;
        case 57: out = 20700; break;
        case 58: out = 11000; break;
        case 59: out = -9000; break;
        case 60: out = -19100; break;
        case 61: out = -19300; break;
        case 62: out = 10600; break;
        case 63: out = -9400; break;
        case 64: out = 901; break;
        case 65: out = 10901; break;
        case 66: out = -9099; break;
        case 67: out = 701; break;
        case 68: out = 10701; break;
        case 69: out = -9299; break;
        case 70: out = 902; break;
        case 71: out = 10902; break;
        case 72: out = -9098; break;
        case 73: out = 702; break;
        case 74: out = 10702; break;
        case 75: out = -9298; break;
        case 76: out = 903; break;
        case 77: out = 10903; break;
        case 78: out = -9097; break;
        case 79: out = 703; break;
        case 80: out = 10703; break;
        case 81: out = -9297; break;
        case 82: out = 904; break;
        case 83: out = 10904; break;
        case 84: out = -9096; break;
        case 85: out = 704; break;
        case 86: out = 10704; break;
        case 87: out = -9296; break;
    }
    return out;
}

/** Machine Generated code, used to map from the offset index into the unique move id/index */
int offset_id_to_index(int offset_id) {
    int out = 0;
    switch (offset_id) {
        case -69200: out = 0; break;
        case 100: out = 1; break;
        case -69900: out = 2; break;
        case -68500: out = 3; break;
        case -59200: out = 4; break;
        case 200: out = 5; break;
        case -59800: out = 6; break;
        case -58600: out = 7; break;
        case -49200: out = 8; break;
        case 300: out = 9; break;
        case -49700: out = 10; break;
        case -48700: out = 11; break;
        case -39200: out = 12; break;
        case 400: out = 13; break;
        case -39600: out = 14; break;
        case -38800: out = 15; break;
        case -29200: out = 16; break;
        case 500: out = 17; break;
        case -29500: out = 18; break;
        case -28900: out = 19; break;
        case -19200: out = 20; break;
        case 600: out = 21; break;
        case -19400: out = 22; break;
        case -19000: out = 23; break;
        case -9200: out = 24; break;
        case 700: out = 25; break;
        case -9300: out = 26; break;
        case -9100: out = 27; break;
        case 10800: out = 28; break;
        case 900: out = 29; break;
        case 10900: out = 30; break;
        case 10700: out = 31; break;
        case 20800: out = 32; break;
        case 1000: out = 33; break;
        case 21000: out = 34; break;
        case 20600: out = 35; break;
        case 30800: out = 36; break;
        case 1100: out = 37; break;
        case 31100: out = 38; break;
        case 30500: out = 39; break;
        case 40800: out = 40; break;
        case 1200: out = 41; break;
        case 41200: out = 42; break;
        case 40400: out = 43; break;
        case 50800: out = 44; break;
        case 1300: out = 45; break;
        case 51300: out = 46; break;
        case 50300: out = 47; break;
        case 60800: out = 48; break;
        case 1400: out = 49; break;
        case 61400: out = 50; break;
        case 60200: out = 51; break;
        case 70800: out = 52; break;
        case 1500: out = 53; break;
        case 71500: out = 54; break;
        case 70100: out = 55; break;
        case 20900: out = 56; break;
        case 20700: out = 57; break;
        case 11000: out = 58; break;
        case -9000: out = 59; break;
        case -19100: out = 60; break;
        case -19300: out = 61; break;
        case 10600: out = 62; break;
        case -9400: out = 63; break;
        case 901: out = 64; break;
        case 10901: out = 65; break;
        case -9099: out = 66; break;
        case 701: out = 67; break;
        case 10701: out = 68; break;
        case -9299: out = 69; break;
        case 902: out = 70; break;
        case 10902: out = 71; break;
        case -9098: out = 72; break;
        case 702: out = 73; break;
        case 10702: out = 74; break;
        case -9298: out = 75; break;
        case 903: out = 76; break;
        case 10903: out = 77; break;
        case -9097: out = 78; break;
        case 703: out = 79; break;
        case 10703: out = 80; break;
        case -9297: out = 81; break;
        case 904: out = 82; break;
        case 10904: out = 83; break;
        case -9096: out = 84; break;
        case 704: out = 85; break;
        case 10704: out = 86; break;
        case -9296: out = 87; break;
    }
    return out;
}

/** Machine Generated code, used to map from the string value for the partial move into an integer */
int move_str_to_rep_int(char *move_str) {
    if (strcmp(move_str, "a1") == 0){return 1;}
    if (strcmp(move_str, "a2") == 0){return 2;}
    if (strcmp(move_str, "a3") == 0){return 3;}
    if (strcmp(move_str, "a4") == 0){return 4;}
    if (strcmp(move_str, "a5") == 0){return 5;}
    if (strcmp(move_str, "a6") == 0){return 6;}
    if (strcmp(move_str, "a7") == 0){return 7;}
    if (strcmp(move_str, "a8") == 0){return 8;}
    if (strcmp(move_str, "b1") == 0){return 9;}
    if (strcmp(move_str, "b2") == 0){return 10;}
    if (strcmp(move_str, "b3") == 0){return 11;}
    if (strcmp(move_str, "b4") == 0){return 12;}
    if (strcmp(move_str, "b5") == 0){return 13;}
    if (strcmp(move_str, "b6") == 0){return 14;}
    if (strcmp(move_str, "b7") == 0){return 15;}
    if (strcmp(move_str, "b8") == 0){return 16;}
    if (strcmp(move_str, "c1") == 0){return 17;}
    if (strcmp(move_str, "c2") == 0){return 18;}
    if (strcmp(move_str, "c3") == 0){return 19;}
    if (strcmp(move_str, "c4") == 0){return 20;}
    if (strcmp(move_str, "c5") == 0){return 21;}
    if (strcmp(move_str, "c6") == 0){return 22;}
    if (strcmp(move_str, "c7") == 0){return 23;}
    if (strcmp(move_str, "c8") == 0){return 24;}
    if (strcmp(move_str, "d1") == 0){return 25;}
    if (strcmp(move_str, "d2") == 0){return 26;}
    if (strcmp(move_str, "d3") == 0){return 27;}
    if (strcmp(move_str, "d4") == 0){return 28;}
    if (strcmp(move_str, "d5") == 0){return 29;}
    if (strcmp(move_str, "d6") == 0){return 30;}
    if (strcmp(move_str, "d7") == 0){return 31;}
    if (strcmp(move_str, "d8") == 0){return 32;}
    if (strcmp(move_str, "e1") == 0){return 33;}
    if (strcmp(move_str, "e2") == 0){return 34;}
    if (strcmp(move_str, "e3") == 0){return 35;}
    if (strcmp(move_str, "e4") == 0){return 36;}
    if (strcmp(move_str, "e5") == 0){return 37;}
    if (strcmp(move_str, "e6") == 0){return 38;}
    if (strcmp(move_str, "e7") == 0){return 39;}
    if (strcmp(move_str, "e8") == 0){return 40;}
    if (strcmp(move_str, "f1") == 0){return 41;}
    if (strcmp(move_str, "f2") == 0){return 42;}
    if (strcmp(move_str, "f3") == 0){return 43;}
    if (strcmp(move_str, "f4") == 0){return 44;}
    if (strcmp(move_str, "f5") == 0){return 45;}
    if (strcmp(move_str, "f6") == 0){return 46;}
    if (strcmp(move_str, "f7") == 0){return 47;}
    if (strcmp(move_str, "f8") == 0){return 48;}
    if (strcmp(move_str, "g1") == 0){return 49;}
    if (strcmp(move_str, "g2") == 0){return 50;}
    if (strcmp(move_str, "g3") == 0){return 51;}
    if (strcmp(move_str, "g4") == 0){return 52;}
    if (strcmp(move_str, "g5") == 0){return 53;}
    if (strcmp(move_str, "g6") == 0){return 54;}
    if (strcmp(move_str, "g7") == 0){return 55;}
    if (strcmp(move_str, "g8") == 0){return 56;}
    if (strcmp(move_str, "h1") == 0){return 57;}
    if (strcmp(move_str, "h2") == 0){return 58;}
    if (strcmp(move_str, "h3") == 0){return 59;}
    if (strcmp(move_str, "h4") == 0){return 60;}
    if (strcmp(move_str, "h5") == 0){return 61;}
    if (strcmp(move_str, "h6") == 0){return 62;}
    if (strcmp(move_str, "h7") == 0){return 63;}
    if (strcmp(move_str, "h8") == 0){return 64;}
    if (strcmp(move_str, "a1r") == 0){return 65;}
    if (strcmp(move_str, "a1n") == 0){return 66;}
    if (strcmp(move_str, "a1b") == 0){return 67;}
    if (strcmp(move_str, "a1q") == 0){return 68;}
    if (strcmp(move_str, "b1r") == 0){return 69;}
    if (strcmp(move_str, "b1n") == 0){return 70;}
    if (strcmp(move_str, "b1b") == 0){return 71;}
    if (strcmp(move_str, "b1q") == 0){return 72;}
    if (strcmp(move_str, "c1r") == 0){return 73;}
    if (strcmp(move_str, "c1n") == 0){return 74;}
    if (strcmp(move_str, "c1b") == 0){return 75;}
    if (strcmp(move_str, "c1q") == 0){return 76;}
    if (strcmp(move_str, "d1r") == 0){return 77;}
    if (strcmp(move_str, "d1n") == 0){return 78;}
    if (strcmp(move_str, "d1b") == 0){return 79;}
    if (strcmp(move_str, "d1q") == 0){return 80;}
    if (strcmp(move_str, "e1r") == 0){return 81;}
    if (strcmp(move_str, "e1n") == 0){return 82;}
    if (strcmp(move_str, "e1b") == 0){return 83;}
    if (strcmp(move_str, "e1q") == 0){return 84;}
    if (strcmp(move_str, "f1r") == 0){return 85;}
    if (strcmp(move_str, "f1n") == 0){return 86;}
    if (strcmp(move_str, "f1b") == 0){return 87;}
    if (strcmp(move_str, "f1q") == 0){return 88;}
    if (strcmp(move_str, "g1r") == 0){return 89;}
    if (strcmp(move_str, "g1n") == 0){return 90;}
    if (strcmp(move_str, "g1b") == 0){return 91;}
    if (strcmp(move_str, "g1q") == 0){return 92;}
    if (strcmp(move_str, "h1r") == 0){return 93;}
    if (strcmp(move_str, "h1n") == 0){return 94;}
    if (strcmp(move_str, "h1b") == 0){return 95;}
    if (strcmp(move_str, "h1q") == 0){return 96;}
    if (strcmp(move_str, "a8r") == 0){return 97;}
    if (strcmp(move_str, "a8n") == 0){return 98;}
    if (strcmp(move_str, "a8b") == 0){return 99;}
    if (strcmp(move_str, "a8q") == 0){return 100;}
    if (strcmp(move_str, "b8r") == 0){return 101;}
    if (strcmp(move_str, "b8n") == 0){return 102;}
    if (strcmp(move_str, "b8b") == 0){return 103;}
    if (strcmp(move_str, "b8q") == 0){return 104;}
    if (strcmp(move_str, "c8r") == 0){return 105;}
    if (strcmp(move_str, "c8n") == 0){return 106;}
    if (strcmp(move_str, "c8b") == 0){return 107;}
    if (strcmp(move_str, "c8q") == 0){return 108;}
    if (strcmp(move_str, "d8r") == 0){return 109;}
    if (strcmp(move_str, "d8n") == 0){return 110;}
    if (strcmp(move_str, "d8b") == 0){return 111;}
    if (strcmp(move_str, "d8q") == 0){return 112;}
    if (strcmp(move_str, "e8r") == 0){return 113;}
    if (strcmp(move_str, "e8n") == 0){return 114;}
    if (strcmp(move_str, "e8b") == 0){return 115;}
    if (strcmp(move_str, "e8q") == 0){return 116;}
    if (strcmp(move_str, "f8r") == 0){return 117;}
    if (strcmp(move_str, "f8n") == 0){return 118;}
    if (strcmp(move_str, "f8b") == 0){return 119;}
    if (strcmp(move_str, "f8q") == 0){return 120;}
    if (strcmp(move_str, "g8r") == 0){return 121;}
    if (strcmp(move_str, "g8n") == 0){return 122;}
    if (strcmp(move_str, "g8b") == 0){return 123;}
    if (strcmp(move_str, "g8q") == 0){return 124;}
    if (strcmp(move_str, "h8r") == 0){return 125;}
    if (strcmp(move_str, "h8n") == 0){return 126;}
    if (strcmp(move_str, "h8b") == 0){return 127;}
    if (strcmp(move_str, "h8q") == 0){return 128;}

    // Default return in case no match is found
    return 0;
}
