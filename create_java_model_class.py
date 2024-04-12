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
def generate_class_content(package_name, class_name, table_name, template):
    return template.format(package=package_name, ClassName=class_name, className=class_name.lower(),
                           TableName=table_name)


# Function to get the directory for a given type
def get_directory(base_directory, type_path):
    return os.path.join(base_directory, *type_path.split('.'))


# Templates for different class types
templates = {
    "model": """package com.example.{package}.model;
import com.example.backendcoreservice.model.AbstractEntity;
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
    "dto": """package com.example.{package}.dto;
import com.example.backendcoreservice.dto.AbstractDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@Data
public class {ClassName}Dto extends AbstractDto {{
private Long id;

}}
""",
    "transformer/mapper": """package com.example.{package}.transformer.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.InjectionStrategy;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.transformer.mapper.AbstractMapper;

@Mapper(componentModel = "spring", injectionStrategy = InjectionStrategy.CONSTRUCTOR)
public interface {ClassName}Mapper extends AbstractMapper<{ClassName}, {ClassName}Dto> {{


}}
""",
    "transformer": """package com.example.{package}.transformer;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import com.example.{package}.transformer.mapper.{ClassName}Mapper;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.transformer.AbstractTransformer;

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
    "dao/repo": """package com.example.{package}.dao.repo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.example.{package}.model.{ClassName};

@Repository
public interface {ClassName}Repo extends JpaRepository<{ClassName}, Long> {{

}}
""",
    "dao": """package com.example.{package}.dao;

import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.dao.AbstractDao;
import com.example.{package}.dao.repo.{ClassName}Repo;

public interface {ClassName}Dao extends AbstractDao<{ClassName}, {ClassName}Repo> {{

}}
""",
    "dao.impl": """package com.example.{package}.dao;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import com.example.{package}.dao.repo.{ClassName}Repo;

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
    "service": """package com.example.{package}.service;

import com.example.{package}.model.{ClassName};
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.transformer.{ClassName}Transformer;
import com.example.{package}.dao.{ClassName}Dao;
import com.example.backendcoreservice.service.AbstractService;

public interface {ClassName}Service extends AbstractService<{ClassName}, {ClassName}Dto, {ClassName}Transformer, {ClassName}Dao> {{

}}
""",
    "service.impl": """package com.example.{package}.service;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.example.{package}.dao.{ClassName}Dao;
import com.example.{package}.transformer.{ClassName}Transformer;

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
    



}}
""",
    "controller": """package com.example.{package}.controller;

import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.service.{ClassName}Service;
import com.example.backendcoreservice.controller.AbstractController;
import com.example.backendcoreservice.api.ApiResponseBuilder;


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


def create_class(class_name, table_name, base_directory, package_name, type_name):
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

    content = generate_class_content(package_name, class_name, table_name, templates[type_name])
    write_file(directory, file_name, content)


def main():
    if len(sys.argv) != 4:
        print("Usage: python create_java_structure.py ModuleName ClassName PackageName")
        sys.exit(1)

    module_name = sys.argv[1]
    class_name = sys.argv[2]
    package_name = sys.argv[3]
    # The base directory now includes the module name dynamically
    base_directory = f"../{module_name}/src/main/java/com/example/"

    # Create each component
    for type_name in templates.keys():
        table_name = camel_to_snake(class_name)
        create_class(class_name, table_name, base_directory, package_name, type_name)

    # Any additional operations or function calls go here


if __name__ == "__main__":
    main()
