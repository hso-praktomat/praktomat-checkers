plugins {
    java
}

val studentDir: String by project
val testDir: String by project
val testFilter: String by project

sourceSets {
    main {
        java.srcDir(studentDir)
    }
    test {
        java.srcDir(studentDir)
        java.srcDir(testDir)
    }
}

buildDir = File(studentDir, "../_build")

repositories {
    mavenCentral()
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.9.0")
    implementation("org.junit.jupiter:junit-jupiter:5.9.0")
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events(
            org.gradle.api.tasks.testing.logging.TestLogEvent.PASSED,
            org.gradle.api.tasks.testing.logging.TestLogEvent.SKIPPED,
            org.gradle.api.tasks.testing.logging.TestLogEvent.FAILED,
            org.gradle.api.tasks.testing.logging.TestLogEvent.STANDARD_ERROR
        )
        showExceptions = true
        exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
        showCauses = true
        showStackTraces = true
    }
    filter {
        includeTestsMatching(testFilter)
    }
}
