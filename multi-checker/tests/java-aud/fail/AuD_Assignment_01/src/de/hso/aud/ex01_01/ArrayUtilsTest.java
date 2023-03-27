package de.hso.aud.ex01_01;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class ArrayUtilsTest {

    @Test
    void testZip() {
        Object[] arr1 = new Object[] {"1", "2", "3"};
        Object[] arr2 = new Object[] {"A", "B", "C", "D"};
        assertArrayEquals(
                new Object[] {"1", "A", "2", "B", "3", "C"},
                ArrayUtils.zip(arr1, arr2)
        );
        // Schreiben Sie zwei weitere Tests
    }

    @Test
    void testEverySecond() {
        int[] arr = new int[] {1,2,3,4,5,6,7,8};
        assertEquals(16, ArrayUtils.sumEverySecond(arr));
    }
    //---
    @Test
    void testSumEverySecond() {
        int[] arr = {1, 2, 3, 4, 5};
        int expected = 9;
        int result = ArrayUtils.sumEverySecond(arr);
        assertEquals(expected, result);
    }
    @Test
    void testSumEverySecondSecondOne() {
    	int[] arr = {5,9,23,128,28,378,923};
    	int expected = 979;
    	int result = ArrayUtils.sumEverySecond(arr);
    	assertEquals(expected, result);
    }

    @Test
    void testZipEmptyArray() {
        Integer[] a1 = {};
        Integer[] a2 = {4, 5, 6, 7};
        Object[] expectedResult = {};
        assertArrayEquals(expectedResult, ArrayUtils.zip(a1, a2));
    }

    @Test
    void testZipEqualLength() {
        Integer[] a1 = {3, 6, 1};
        Integer[] a2 = {9, 1, 1};
        Object[] expectedResult = {3,9,6,1,1,1};

        
        assertArrayEquals(expectedResult, ArrayUtils.zip(a1, a2));
       
    }
    // ergänzen Sie einen Test für reverse
    @Test
    void testReverseNew(){
    	Integer[] array = {3,6,6,1,9,1,1};
    	Integer[] expectedResult = {1,1,9,1,6,6,3};
    	ArrayUtils.reverse(array);
    	assertArrayEquals(array, expectedResult);
    }
}