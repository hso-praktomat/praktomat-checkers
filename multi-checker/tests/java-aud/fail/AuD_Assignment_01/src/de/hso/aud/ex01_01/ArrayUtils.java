package de.hso.aud.ex01_01;

public class ArrayUtils {

    public static Object[] zip(Object[] arr1, Object[] arr2) {

        //erst die kleinste Länge herausfinden
        //denn w ir brauchen im Notfall die Länge vom kürzeren Array
        //Beschreibung von Docs.Oracle.com:
        //      Returns the smaller of two int values.
        int kleinsteLaenge = Math.min(arr1.length, arr2.length);
        Object[] result = new Object[kleinsteLaenge * 2];

        for (int i = 0; i < kleinsteLaenge; i++) {
           result[i * 2] = arr1[i];
            result[i * 2 + 1] = arr2[i];
        }

        return result;
    }

    public static int sumEverySecond(int[] arr) {
        int j =0;
        int sumAktuell = 0;
        // statt i++, i+=2 nehmen, damit jede zweite Stelle
        //summiert wird
        while (j < arr.length) {
            sumAktuell += arr[j];
            // j +=2;
            j = j + 2;
        }
        // sumAktuell wieder ausgeben
        return sumAktuell;
    }

    public static void reverse(Object[] arr) {
        // mit right die eigentliche Länge vom Array
        // herausfinden, dann Mithilfe der For-Schleife
        // die zwei int Parameter gegeneinander laufen lassen
        int right = arr.length - 1;

        for(int left = 0; left < right; left++) {
            Object temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            right--;
        }
    }
}
