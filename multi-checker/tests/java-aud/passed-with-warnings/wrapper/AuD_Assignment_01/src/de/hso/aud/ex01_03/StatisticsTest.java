package de.hso.aud.ex01_03;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class StatisticsTest {

    // Fügen Sie jeweils einen Test hinzu.
    
    @Test
    void testMedian() {
        double[] arr = new double[] {10, 5.5, 2, -5, 8, 7};
        assertEquals(6.25, Statistics.median(arr), 0.000001);
    }

    @Test
    void testMean() {
        double[] arr = new double[] {10, 5.5, 2, -5, 8, 7};
        assertEquals(4.5833333, Statistics.mean(arr), 0.0001);
    }
    
    @Test
    void testQuantile() {
        double[] arr = new double[] {10, 5, 29, 0, 11, 6, 56, -4, 0, 31};
        assertEquals(0, Statistics.quantile(25, arr));
        assertEquals(56, Statistics.quantile(90, arr));
    }
}
