# 📝 Instrucciones para Actualizar el Notebook de Colab

## ⚠️ IMPORTANTE: Actualiza la función `upload_chunks_to_supabase`

Después de ejecutar `RECREAR_TABLA_SUPABASE.sql` en Supabase, necesitas actualizar la función en el notebook.

### 🔧 Pasos:

1. **Abre tu notebook en Colab**
2. **Encuentra la celda que contiene la función `upload_chunks_to_supabase`** (Celda 16: "8️⃣ Conexión y Operaciones con Supabase")
3. **Reemplaza la función completa con esta versión simplificada:**

```python
def upload_chunks_to_supabase(chunks: List[Dict], embeddings: List[List[float]], batch_size: int = 10) -> int:
    """
    Subir chunks y embeddings a Supabase con estructura correcta
    Estructura esperada: id, vec, document, metadata
    """
    conn = None
    cursor = None
    uploaded = 0
    total_chunks = len(chunks)
    
    try:
        # Obtener conexión
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que la tabla tiene la estructura correcta
        columns = get_table_columns(conn, COLLECTION_NAME)
        has_document = 'document' in columns
        has_vec = 'vec' in columns
        
        if not has_document:
            raise ValueError(f"❌ La tabla {COLLECTION_NAME} no tiene la columna 'document'. Ejecuta RECREAR_TABLA_SUPABASE.sql primero.")
        if not has_vec:
            raise ValueError(f"❌ La tabla {COLLECTION_NAME} no tiene la columna 'vec'. Ejecuta RECREAR_TABLA_SUPABASE.sql primero.")
        
        print(f"📋 Estructura correcta detectada: id, vec, document, metadata")
        print(f"📤 Subiendo {total_chunks} chunks a Supabase...")
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            print(f"  📦 Procesando batch {batch_num}/{total_batches}...")
            
            batch_uploaded = 0
            batch_errors = 0
            
            for chunk, embedding in zip(batch_chunks, batch_embeddings):
                try:
                    # Verificar que la conexión esté viva
                    if conn.closed:
                        print(f"  🔄 Reconectando...")
                        if cursor:
                            cursor.close()
                        conn.close()
                        conn = get_connection()
                        cursor = conn.cursor()
                    
                    chunk_id = f"{Path(chunk['metadata']['file_name']).stem}_{chunk['metadata'].get('chunk_index', i)}"
                    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                    chunk_metadata = chunk['metadata'].copy()
                    metadata_json = json.dumps(chunk_metadata)
                    
                    # Insertar con estructura correcta: id, vec, document, metadata
                    cursor.execute(f"""
                        INSERT INTO vecs.{COLLECTION_NAME}
                        (id, vec, document, metadata)
                        VALUES (%s, %s::vector, %s, %s::jsonb)
                        ON CONFLICT (id) DO UPDATE SET
                            vec = EXCLUDED.vec,
                            document = EXCLUDED.document,
                            metadata = EXCLUDED.metadata;
                    """, (chunk_id, embedding_str, chunk['text'], metadata_json))
                    
                    batch_uploaded += 1
                    uploaded += 1
                    
                except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                    # Error de conexión - intentar reconectar
                    logger.warning(f"⚠️ Error de conexión en chunk {chunk_id}: {e}")
                    batch_errors += 1
                    try:
                        if cursor:
                            cursor.close()
                        conn.close()
                    except:
                        pass
                    
                    # Reconectar y reintentar
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        print(f"  🔄 Reconectado, reintentando chunk...")
                        
                        chunk_id = f"{Path(chunk['metadata']['file_name']).stem}_{chunk['metadata'].get('chunk_index', i)}"
                        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                        chunk_metadata = chunk['metadata'].copy()
                        metadata_json = json.dumps(chunk_metadata)
                        
                        cursor.execute(f"""
                            INSERT INTO vecs.{COLLECTION_NAME}
                            (id, vec, document, metadata)
                            VALUES (%s, %s::vector, %s, %s::jsonb)
                            ON CONFLICT (id) DO UPDATE SET
                                vec = EXCLUDED.vec,
                                document = EXCLUDED.document,
                                metadata = EXCLUDED.metadata;
                        """, (chunk_id, embedding_str, chunk['text'], metadata_json))
                        
                        batch_uploaded += 1
                        uploaded += 1
                    except Exception as retry_error:
                        logger.error(f"❌ Error en reintento: {retry_error}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error subiendo chunk {chunk_id}: {e}")
                    batch_errors += 1
                    continue
            
            # Commit del batch
            try:
                if not conn.closed:
                    conn.commit()
                    if batch_errors > 0:
                        print(f"  ⚠️ Batch {batch_num} completado ({batch_uploaded}/{len(batch_chunks)} chunks, {batch_errors} errores)")
                    else:
                        print(f"  ✅ Batch {batch_num} completado ({batch_uploaded}/{len(batch_chunks)} chunks)")
                else:
                    print(f"  ⚠️ Conexión cerrada, saltando commit del batch {batch_num}")
            except Exception as e:
                logger.error(f"❌ Error en commit del batch {batch_num}: {e}")
                try:
                    conn.rollback()
                except:
                    pass
        
        print(f"✅ Subida completada: {uploaded}/{total_chunks} chunks")
        return uploaded
        
    except Exception as e:
        logger.error(f"❌ Error subiendo a Supabase: {e}")
        raise
    finally:
        # Cerrar conexiones
        try:
            if cursor:
                cursor.close()
            if conn and not conn.closed:
                conn.close()
        except:
            pass
```

### ✅ Cambios principales:

1. **Eliminada toda la lógica condicional** - Ahora siempre usa la estructura: `id, vec, document, metadata`
2. **Validación de estructura** - Verifica que la tabla tenga las columnas correctas antes de insertar
3. **Código simplificado** - Mucho más fácil de mantener y entender
4. **Mensajes de error claros** - Indica exactamente qué falta si la tabla no tiene la estructura correcta

### 📋 Orden de ejecución:

1. ✅ Ejecuta `RECREAR_TABLA_SUPABASE.sql` en Supabase SQL Editor
2. ✅ Actualiza la función en el notebook (código arriba)
3. ✅ Ejecuta el notebook para procesar tus documentos
4. ✅ El bot en Railway debería funcionar correctamente ahora

