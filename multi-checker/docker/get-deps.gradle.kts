plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.andrewoma.dexx:collection:0.7")
    implementation("org.junit.jupiter:junit-jupiter:5.10.2")
    implementation("junit:junit:4.13.2")
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
