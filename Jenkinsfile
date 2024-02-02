pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = "the127terminal"
        APP_NAME = "score"
        IMAGE_TAG = "${BUILD_NUMBER}"
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/${APP_NAME}" 
        REGISTRY_CREDS = 'dockerhub'
    }

    stages {
        stage('Cleanup workspace') {
            steps {
                script {
                    cleanWs()
                }
            }
        }

        stage('Pull docker image') {
            steps {
                script {
                    git credentialsId: 'github',
                        url: 'https://github.com/Terminal127/score-keeper',
                        branch: 'main'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonar'
                    withSonarQubeEnv('sonar') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Create Playbook') {
            steps {
                script {
                    writeFile file: 'play.yml', text: '''
---
- hosts: localhost
  become: true

  vars:
    dockerhub_username: usernamehere
    dockerhub_password: passwordhere

  tasks:
    - name: Ensure Docker is installed
      become: true
      apt:
        name: docker.io
        state: present
      tags:
        - docker

    - name: Build Docker image
      community.docker.docker_image:
        name: the127terminal/score
        tag: latest
        build:
          path: /home/ubuntu
        source: build
      tags:
        - docker

    - name: Log Docker Hub credentials
      shell: 'echo "Docker Hub Username: {{ dockerhub_username }}" > /home/ubuntu/docker_credentials.txt && echo "Docker Hub Password: {{ dockerhub_password }}" >> /home/ubuntu/docker_credentials.txt'
      tags:
        - docker

    - name: Log in to Docker Hub
      docker_login:
        username: "{{ dockerhub_username }}"
        password: "{{ dockerhub_password }}"
      tags:
        - docker

    - name: Push Docker image to Docker Hub
      community.docker.docker_image_push:
        name: the127terminal/score
        tag: latest
      tags:
        - docker
'''
                }
            }
        }
        stage('adding creds to the file.yml') {
            steps {
                script {

                    // Change the working directory to the 'manifests' director
                        withCredentials([string(credentialsId: 'auth', variable: 'DOCKERHUB_PASSWORD')]) {
                        sh "sed -i 's|tag: .*|tag: ${IMAGE_TAG}|g' play.yml"
                        sh "sed -i 's|dockerhub_username: usernamehere|dockerhub_username: ${DOCKERHUB_USERNAME}|' play.yml"
                        sh "sed -i 's|dockerhub_password: passwordhere|dockerhub_password: ${DOCKERHUB_PASSWORD}|' play.yml"
                        }
                }
            }
        }


        stage('Push Docker image using Ansible') {
            steps {
                script {
                    sshPublisher(publishers: 
                    [sshPublisherDesc(configName: 'ansi', sshCredentials:
                    [encryptedPassphrase: '{AQAAABAAAAAQ4QqWXL9q5lm5O8jcSjLVEB8s+ObCpzrFIjb7OyRsdgc=}', key: '', keyPath: '', username: 'ubuntu'],
                     transfers: 
                    [sshTransfer(cleanRemote: false,
                     excludes: '',
                       execCommand: 'ansible-playbook -i inventory.ini play.yml ; docker rmi -f $(docker images -q) ; rm -rf *',
                       execTimeout: 120000,
                        flatten: false,
                         makeEmptyDirs: true,
                          noDefaultExcludes: false,
                            patternSeparator: '[, ]+',
                             remoteDirectory: '//home//ubuntu//',
                                remoteDirectorySDF: false,
                                 removePrefix: '',
                        sourceFiles: '**/*')],
                        usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: true)
                                ])
                }
            }
        }


        // stage('Delete docker image') {
        //     steps {
        //         script {
        //             def lowercaseTag = IMAGE_TAG.toLowerCase()
        //             def dockerImageNameWithTag = "${IMAGE_NAME}:${lowercaseTag}"

        //             sh "docker rmi ${dockerImageNameWithTag}"
        //             sh "docker rmi registry.hub.docker.com/${DOCKERHUB_USERNAME}/${APP_NAME}:${BUILD_NUMBER}"
        //         }
        //     }
        // }

        stage('Updating the manifests') {
            steps {
                script {
                    def lowercaseTag = IMAGE_TAG.toLowerCase()
                    def dockerImageNameWithTag = "${IMAGE_NAME}:${lowercaseTag}"

                    // Change the working directory to the 'manifests' directory
                    dir('manifests') {
                        sh "pwd"
                        echo "Contents of the current directory:"
                        sh 'ls -al'
                        sh "git checkout release"
                        sh "sed -i 's|image: ${DOCKERHUB_USERNAME}/${APP_NAME}:.*|image: ${DOCKERHUB_USERNAME}/${APP_NAME}:${IMAGE_TAG}|g' flask-deployment.yaml"
                    }
                }
            }
        }

        stage('Push to repository') {
            steps {
                script {
                    // Change the working directory to the 'manifests' directory
                    dir('manifests') {
                        sh "git config --global user.name 'Terminal127'"
                        sh "git config --global user.email 'terminalishere127@gmail.com'"
                        
                        sh "git add flask-deployment.yaml"
                        sh "git commit -m 'updated flask-deployment.yaml'"
                        
                        // Use credentials for authentication
                        withCredentials([gitUsernamePassword(credentialsId: 'github')]) {
                            sh "git push https://github.com/Terminal127/score-keeper release"
                        }
                    }
                }
            }
        }
    }
}
