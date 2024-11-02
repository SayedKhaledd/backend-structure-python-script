import os
import re
import sys


# Function to create directory and file, then write the content
def write_file(directory, file_name, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, file_name), "w") as file:
        file.write(content)
    print(f"{file_name} has been created in {directory}")


# Function to generate class contents for various components
def generate_class_content(package_name, class_name, table_name, template, artifact_id):
    return template.format(package=package_name, ClassName=class_name, className=class_name.lower(),
                           TableName=table_name, artifactId=artifact_id)


# Function to get the directory for a given type
def get_directory(base_directory, type_path):
    return os.path.join(base_directory, *type_path.split('.'))


# Templates for different class types
templates = {
    "model": """package {artifactId}.{package}.model;
import {artifactId}.backendcoreservice.model.AbstractEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;


@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@Data
@Entity
@Table(name = "{TableName}")
public class {ClassName} extends AbstractEntity {{
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "{TableName}_id_sequence")
    @SequenceGenerator(name = "{TableName}_id_sequence", sequenceName = "{TableName}_id_sequence", allocationSize = 1)
    private Long id;

}}
""",
    "dto": """package {artifactId}.{package}.dto;
import {artifactId}.backendcoreservice.dto.AbstractDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@SuperBuilder(toBuilder = true, builderMethodName = "{ClassName}DtoBuilder")
@Data
public class {ClassName}Dto extends AbstractDto {{
private Long id;

}}
""",
    "transformer/mapper": """package {artifactId}.{package}.transformer.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.InjectionStrategy;
import {artifactId}.{package}.dto.{ClassName}Dto;
import {artifactId}.{package}.model.{ClassName};
import {artifactId}.backendcoreservice.transformer.mapper.AbstractMapper;

@Mapper(componentModel = "spring", injectionStrategy = InjectionStrategy.CONSTRUCTOR)
public interface {ClassName}Mapper extends AbstractMapper<{ClassName}, {ClassName}Dto> {{


}}
""",
    "transformer": """package {artifactId}.{package}.transformer;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import {artifactId}.{package}.transformer.mapper.{ClassName}Mapper;
import {artifactId}.{package}.dto.{ClassName}Dto;
import {artifactId}.{package}.model.{ClassName};
import {artifactId}.backendcoreservice.transformer.AbstractTransformer;

@Component
@AllArgsConstructor
public class {ClassName}Transformer implements AbstractTransformer<{ClassName}, {ClassName}Dto, {ClassName}Mapper> {{

    private final {ClassName}Mapper {className}Mapper;

    @Override
    public {ClassName}Mapper getMapper() {{
        return {className}Mapper;
    }}


}}
""",
    "dao/repo": """package {artifactId}.{package}.dao.repo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import {artifactId}.{package}.model.{ClassName};

@Repository
public interface {ClassName}Repo extends JpaRepository<{ClassName}, Long> {{

}}
""",
    "dao": """package {artifactId}.{package}.dao;

import {artifactId}.{package}.model.{ClassName};
import {artifactId}.backendcoreservice.dao.AbstractDao;
import {artifactId}.{package}.dao.repo.{ClassName}Repo;

public interface {ClassName}Dao extends AbstractDao<{ClassName}, {ClassName}Repo> {{

}}
""",
    "dao.impl": """package {artifactId}.{package}.dao;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import {artifactId}.{package}.dao.repo.{ClassName}Repo;

@Component
@AllArgsConstructor
public class {ClassName}DaoImpl implements {ClassName}Dao {{

    private final {ClassName}Repo {className}Repo;

    @Override
    public {ClassName}Repo getRepo() {{
        return {className}Repo;
    }}


}}
""",
    "service": """package {artifactId}.{package}.service;

import {artifactId}.{package}.model.{ClassName};
import {artifactId}.{package}.dto.{ClassName}Dto;
import {artifactId}.{package}.transformer.{ClassName}Transformer;
import {artifactId}.{package}.dao.{ClassName}Dao;
import {artifactId}.backendcoreservice.service.AbstractService;

public interface {ClassName}Service extends AbstractService<{ClassName}, {ClassName}Dto, {ClassName}Transformer, {ClassName}Dao> {{

}}
""",
    "service.impl": """package {artifactId}.{package}.service;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import {artifactId}.{package}.dao.{ClassName}Dao;
import {artifactId}.{package}.transformer.{ClassName}Transformer;
import {artifactId}.{package}.model.{ClassName};


@Slf4j
@Service
@AllArgsConstructor
public class {ClassName}ServiceImpl implements {ClassName}Service {{

    private final {ClassName}Dao {className}Dao;
    private final {ClassName}Transformer {className}Transformer;

    @Override
    public {ClassName}Dao getDao() {{
        return {className}Dao;
    }}

    @Override
    public {ClassName}Transformer getTransformer() {{
        return {className}Transformer;
    }}
    
    @Override
    public String getEntityName() {{
       return {ClassName}.class.getSimpleName();
    }}
    



}}
""",
    "controller": """package {artifactId}.{package}.controller;

import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import {artifactId}.{package}.dto.{ClassName}Dto;
import {artifactId}.{package}.service.{ClassName}Service;
import {artifactId}.backendcoreservice.controller.AbstractController;
import {artifactId}.backendcoreservice.api.ApiResponseBuilder;


@RestController
@RequestMapping("/api/{className}")
@AllArgsConstructor
public class {ClassName}Controller implements AbstractController<{ClassName}Service, {ClassName}Dto> {{

    private final {ClassName}Service {className}Service;
    private final ApiResponseBuilder<{ClassName}Dto> apiResponseBuilder;


    @Override
    public {ClassName}Service getService() {{
        return {className}Service;
    }}
    
    @Override
    public ApiResponseBuilder<{ClassName}Dto> getApiResponseBuilder() {{
    return apiResponseBuilder;
    }}





}}
"""
}


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def create_class(class_name, table_name, base_directory, package_name, type_name, artifact_id):
    # Special handling for 'dao.impl' to avoid creating an 'impl' package
    if type_name == "dao.impl":
        directory = get_directory(base_directory, f"{package_name}.dao")
        file_name = f"{class_name}DaoImpl.java"

    elif type_name == "service.impl":
        directory = get_directory(base_directory, f"{package_name}.service")
        file_name = f"{class_name}ServiceImpl.java"
    elif type_name == "model":
        directory = get_directory(base_directory, f"{package_name}.model")
        file_name = f"{class_name}.java"
    else:
        directory = get_directory(base_directory, f"{package_name}.{type_name}")
        file_name = f"{class_name}{type_name.split('/')[-1].capitalize()}.java"

    content = generate_class_content(package_name, class_name, table_name, templates[type_name], artifact_id)
    write_file(directory, file_name, content)


def main():
    print(len(sys.argv))
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("Usage: python create_java_structure.py ModuleName ClassName PackageName")
        sys.exit(1)

    module_name = sys.argv[1]
    class_name = sys.argv[2]
    package_name = sys.argv[3]
    # add optional parameter for artifactId
    if len(sys.argv) == 5:
        artifact_id = sys.argv[4]
    else:
        artifact_id = "com.example"

    # The base directory now includes the module name dynamically
    first_part_of_artifact_id = artifact_id.split('.')[0]
    second_part_of_artifact_id = artifact_id.split('.')[1]
    base_directory = f"../{module_name}/src/main/java/{first_part_of_artifact_id}/{second_part_of_artifact_id}/"

    # Create each component
    for type_name in templates.keys():
        table_name = camel_to_snake(class_name)
        create_class(class_name, table_name, base_directory, package_name, type_name, artifact_id)

    # Any additional operations or function calls go here


if __name__ == "__main__":
    main()
