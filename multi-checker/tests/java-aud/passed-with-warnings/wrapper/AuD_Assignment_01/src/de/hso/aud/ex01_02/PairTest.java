package de.hso.aud.ex01_02;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import java.util.*;

class PairTest {

    @Test
    void testFindInversePairs() {
        List<Pair> expected = new ArrayList<Pair>();
        expected.add(new Pair(0, 2));
        expected.add(new Pair(2, 5));
        expected.add(new Pair(3, 4));
        int[] arr = new int[] {2, 3, -2, 0, 0, 2};
        assertEquals(expected, Pair.findInversePairs(arr));
    }
    
    // fügen Sie einen weiteren Test hinzu

}
