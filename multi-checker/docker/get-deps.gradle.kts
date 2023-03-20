plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.junit.jupiter:junit-jupiter:5.9.0")
}

tasks.register<Copy>("getDeps") {
    val mainSource = sourceSets.main.get()
    from(mainSource.compileClasspath, mainSource.runtimeClasspath)
    into("runtime/")

    doFirst {
        delete("runtime")
        mkdir("runtime")
    }

    doLast {
        delete("runtime")
    }
}
